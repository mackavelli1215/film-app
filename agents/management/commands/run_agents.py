"""
Django management command to run agent jobs.
Usage: python manage.py run_agents
"""
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from agents.models import AgentJob
from agents.processors import AgentProcessor


class Command(BaseCommand):
    help = 'Run queued agent jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once instead of continuously',
        )
        parser.add_argument(
            '--sleep',
            type=int,
            default=5,
            help='Sleep time between checks in seconds (default: 5)',
        )

    def handle(self, *args, **options):
        processor = AgentProcessor()
        sleep_time = options['sleep']
        run_once = options['once']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting agent processor (sleep: {sleep_time}s, once: {run_once})')
        )
        
        while True:
            try:
                # Get oldest queued job
                job = AgentJob.objects.filter(status='queued').order_by('created_at').first()
                
                if job:
                    self.stdout.write(f'Processing job {job.id}: {job.agent_type}')
                    
                    # Update job status
                    job.status = 'processing'
                    job.started_at = timezone.now()
                    job.save()
                    
                    try:
                        # Process the job
                        result = processor.process_job(job)
                        
                        if result['success']:
                            job.status = 'completed'
                            job.output_data = result['data']
                            job.error_message = None
                            self.stdout.write(
                                self.style.SUCCESS(f'Job {job.id} completed successfully')
                            )
                        else:
                            job.status = 'failed'
                            job.error_message = result['error']
                            self.stdout.write(
                                self.style.ERROR(f'Job {job.id} failed: {result["error"]}')
                            )
                    
                    except Exception as e:
                        job.status = 'failed'
                        job.error_message = str(e)
                        self.stdout.write(
                            self.style.ERROR(f'Job {job.id} failed with exception: {str(e)}')
                        )
                    
                    finally:
                        job.completed_at = timezone.now()
                        job.save()
                        
                        # Log activity
                        from collab.models import ActivityLog
                        ActivityLog.objects.create(
                            project=job.project,
                            action_type='generate',
                            section=job.agent_type,
                            description=f'Agent job {job.agent_type} {job.status}'
                        )
                
                else:
                    if run_once:
                        self.stdout.write('No jobs to process. Exiting.')
                        break
                    else:
                        self.stdout.write(f'No jobs queued. Sleeping for {sleep_time}s...')
                
                if run_once:
                    break
                
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Shutting down agent processor...'))
                break
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Unexpected error: {str(e)}')
                )
                if run_once:
                    break
                time.sleep(sleep_time)