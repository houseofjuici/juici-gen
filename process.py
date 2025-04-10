from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from datetime import datetime
from praisonai_tools import ProcessTool

class ProcessStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessManager:
    def __init__(self):
        self.processes: Dict[str, Dict[str, Any]] = {}
        self.task_queue = asyncio.Queue()
        self.running = False
        self.process_tool = ProcessTool()

    async def start(self):
        """Start the process manager."""
        if not self.running:
            self.running = True
            asyncio.create_task(self._process_queue())

    async def stop(self):
        """Stop the process manager."""
        self.running = False
        await self.task_queue.join()

    async def create_process(self, task: Dict[str, Any]) -> str:
        """Create a new process and add it to the queue."""
        process_id = f"process_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.processes[process_id] = {
            "id": process_id,
            "task": task,
            "status": ProcessStatus.PENDING,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "result": None,
            "error": None
        }
        
        await self.task_queue.put(process_id)
        return process_id

    async def get_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get process information by ID."""
        return self.processes.get(process_id)

    async def list_processes(self, status: Optional[ProcessStatus] = None) -> List[Dict[str, Any]]:
        """List all processes, optionally filtered by status."""
        if status:
            return [p for p in self.processes.values() if p["status"] == status]
        return list(self.processes.values())

    async def _process_queue(self):
        """Process tasks from the queue."""
        while self.running:
            try:
                process_id = await self.task_queue.get()
                process = self.processes[process_id]
                
                try:
                    process["status"] = ProcessStatus.RUNNING
                    process["updated_at"] = datetime.now()
                    
                    # Process the task using PraisonAI's process tool
                    result = await self.process_tool.execute_task(process["task"])
                    
                    process["status"] = ProcessStatus.COMPLETED
                    process["result"] = result
                except Exception as e:
                    process["status"] = ProcessStatus.FAILED
                    process["error"] = str(e)
                finally:
                    process["updated_at"] = datetime.now()
                    self.task_queue.task_done()
            
            except Exception as e:
                print(f"Error processing queue: {e}")
                await asyncio.sleep(1) 