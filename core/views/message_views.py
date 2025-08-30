"""
Message ingestion and processing views.
Refactored for better separation of concerns and error handling.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.services.message_services import ingest_message
from core.services.wellbeing_service import get_team_wellbeing
from core.exceptions import AuthorizationError, ValidationError, MessageProcessingError
from core.tasks.message_analysis_tasks import process_message_analysis
from core.serializers.message_serializers import MessageIngestionSerializer
from core.utils.response_builder import APIResponseBuilder, created_response, error_response
from core.utils.validators import DateValidator
import logging
import datetime
from dateutil.parser import isoparse

logger = logging.getLogger(__name__)


class MessageView(APIView):
    """
    Handle message ingestion from external services.
    Supports both single messages and batch processing.
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        """
        Ingest messages for analysis.
        Accepts single message or array of messages.
        """
        try:
            # Normalize input to list
            messages_data = request.data if isinstance(request.data, list) else [request.data]
            
            # Validate input
            if not messages_data:
                return APIResponseBuilder.validation_error("No message data provided")
            
            # Validate with serializer
            serializer = MessageIngestionSerializer(data=messages_data, many=True)
            if not serializer.is_valid():
                return APIResponseBuilder.validation_error(
                    message="Message validation failed",
                    errors=serializer.errors
                )
            
            # Process messages
            processed_messages = []
            for data in serializer.validated_data:
                try:
                    message_id = ingest_message(data)
                    
                    # Queue for async ML analysis
                    process_message_analysis.delay(message_id)
                    
                    processed_messages.append({
                        'message_id': message_id,
                        'external_ref': data.get('external_ref'),
                        'status': 'queued_for_analysis'
                    })
                    
                    logger.info(f"Message {message_id} ingested and queued for analysis")
                    
                except Exception as msg_error:
                    logger.error(f"Failed to process message {data.get('external_ref', 'unknown')}: {str(msg_error)}")
                    processed_messages.append({
                        'external_ref': data.get('external_ref'),
                        'status': 'failed',
                        'error': str(msg_error)
                    })
            
            # Return response
            success_count = len([m for m in processed_messages if m.get('status') == 'queued_for_analysis'])
            failed_count = len(processed_messages) - success_count
            
            response_data = {
                'processed_messages': processed_messages,
                'summary': {
                    'total_messages': len(processed_messages),
                    'successful': success_count,
                    'failed': failed_count
                }
            }
            
            if failed_count > 0:
                message = f"Processed {success_count}/{len(processed_messages)} messages successfully"
                return APIResponseBuilder.success(
                    data=response_data,
                    message=message,
                    status_code=status.HTTP_207_MULTI_STATUS
                )
            else:
                return created_response(
                    data=response_data,
                    message=f"All {success_count} messages ingested successfully"
                )
                
        except ValidationError as e:
            return APIResponseBuilder.validation_error(e.message)
        except Exception as e:
            logger.error(f"Unexpected error in message ingestion: {str(e)}")
            return APIResponseBuilder.internal_error(
                message="Failed to process messages",
                error_details=str(e)
            )


class TeamWellbeingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            # Parse and validate dates
            try:
                start_date = isoparse(start_date_str).replace(tzinfo=datetime.timezone.utc) if start_date_str else None
                end_date = isoparse(end_date_str).replace(tzinfo=datetime.timezone.utc) if end_date_str else None
            except ValueError:
                return Response({"error": "Invalid date format. Use ISO 8601 (e.g., 2025-08-30T00:00:00Z)"}, status=status.HTTP_400_BAD_REQUEST)

            if start_date and end_date and start_date > end_date:
                return Response({"error": "start_date must be before end_date"}, status=status.HTTP_400_BAD_REQUEST)

            data = get_team_wellbeing(request.user, start_date, end_date)
            return Response(data, status=status.HTTP_200_OK)
        except AuthorizationError as e:
            return Response({"error": e.message}, status=e.status_code)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        