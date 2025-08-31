"""
Django management command to sync messages without MessageAnalysis instances.
This command finds all messages that don't have corresponding analysis and processes them.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models.message_model import Message, MessageAnalysis
from core.services.model_services import detect_sentiment, detect_emotion, detect_stress
from core.exceptions import MessageProcessingError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync messages without MessageAnalysis by running analysis on them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually processing',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of messages to process (default: all)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Process messages in batches (default: 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        batch_size = options['batch_size']

        self.stdout.write(
            self.style.SUCCESS('Starting message analysis sync...')
        )

        # Find messages without analysis
        messages_without_analysis = Message.objects.exclude(
            id__in=MessageAnalysis.objects.values('message_id')
        ).order_by('created_at')

        if limit:
            messages_without_analysis = messages_without_analysis[:limit]

        total_count = messages_without_analysis.count()

        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ All messages already have analysis!')
            )
            return

        self.stdout.write(
            f'Found {total_count} messages without analysis'
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN - No actual processing will be done')
            )
            for message in messages_without_analysis[:10]:  # Show first 10
                self.stdout.write(f'  - Message {message.id}: "{message.message[:50]}..."')
            if total_count > 10:
                self.stdout.write(f'  ... and {total_count - 10} more messages')
            return

        # Process messages in batches
        processed_count = 0
        failed_count = 0

        for i in range(0, total_count, batch_size):
            batch = messages_without_analysis[i:i + batch_size]
            
            self.stdout.write(
                f'Processing batch {i//batch_size + 1} '
                f'({i + 1} to {min(i + batch_size, total_count)} of {total_count})...'
            )

            for message in batch:
                try:
                    self.process_message(message)
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        self.stdout.write(f'  Processed {processed_count} messages...')

                except Exception as e:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Failed to process message {message.id}: {str(e)}')
                    )
                    logger.error(f'Failed to process message {message.id}: {str(e)}')

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Sync completed!\n'
                f'  Processed: {processed_count}\n'
                f'  Failed: {failed_count}\n'
                f'  Total: {total_count}'
            )
        )

        if failed_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ {failed_count} messages failed to process. Check logs for details.'
                )
            )

    def process_message(self, message):
        """Process a single message and create its analysis."""
        try:
            with transaction.atomic():
                # Update processing status
                message.processing_status = 'processing'
                message.save(update_fields=['processing_status'])

                # Run ML analysis
                sentiment, sentiment_score = detect_sentiment(message.message)
                emotion, emotion_score = detect_emotion(message.message)
                stress_label, stress_score = detect_stress(message.message)

                # Create analysis
                MessageAnalysis.objects.create(
                    message=message,
                    sentiment=sentiment,
                    sentiment_score=sentiment_score,
                    emotion=emotion,
                    emotion_score=emotion_score,
                    stress=stress_label,
                    stress_score=stress_score,
                    sentiment_confidence=1.0,
                    emotion_confidence=1.0,
                    stress_confidence=1.0
                )

                # Mark as completed
                message.processing_status = 'completed'
                message.save(update_fields=['processing_status'])

        except Exception as e:
            # Mark as failed
            try:
                message.processing_status = 'failed'
                message.save(update_fields=['processing_status'])
            except Exception:
                pass
            raise MessageProcessingError(f'Failed to process message: {str(e)}')