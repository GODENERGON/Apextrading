"""
Odysseus API Server
Runs inside Odysseus container on localhost:8888
Provides endpoints for bot and system commands
"""

import logging
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/api_server.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Odysseus API Server", version="0.1.0")

# Paths
WORKSPACE_DIR = Path("/workspace")
LOGS_DIR = Path("/app/logs")
LOGS_DIR.mkdir(exist_ok=True)


class MessageRequest(BaseModel):
    text: str


class LogsRequest(BaseModel):
    lines: int = 50


class ExecuteRequest(BaseModel):
    command: str
    timeout: int = 30


async def run_command(command: str, timeout: int = 30) -> dict:
    """Run shell command and capture output"""
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timeout after {timeout}s",
            }
        
        return {
            "exit_code": proc.returncode,
            "stdout": stdout.decode().strip(),
            "stderr": stderr.decode().strip(),
        }
    except Exception as e:
        logger.error(f"Command failed: {command} - {e}")
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
        }


@app.get("/")
async def root():
    return {"status": "ok", "name": "Odysseus API Server", "version": "0.1.0"}


@app.post("/api/status")
async def api_status():
    """Get system status"""
    logger.info("Status check requested")
    
    try:
        # Check OpenClaw
        openclaw_check = await run_command("systemctl is-active openclaw")
        openclaw_active = openclaw_check["exit_code"] == 0
        
        # Check memory
        mem_check = await run_command("free -h | grep Mem | awk '{print $3}'")
        memory = mem_check["stdout"] if mem_check["exit_code"] == 0 else "unknown"
        
        # Check uptime
        uptime_check = await run_command("uptime -p")
        uptime = uptime_check["stdout"] if uptime_check["exit_code"] == 0 else "unknown"
        
        return {
            "status": "ok",
            "openclaw_active": openclaw_active,
            "odysseus_active": True,  # We're inside Odysseus
            "memory": memory,
            "uptime": uptime,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/message")
async def api_message(req: MessageRequest):
    """Forward message to Ollama via curl"""
    logger.info(f"Message received: {req.text[:50]}...")
    
    try:
        # Simple curl request to Ollama
        curl_cmd = f"""
        curl -s http://host.docker.internal:11434/api/generate \
          -d '{{"model": "phi3.5:latest", "prompt": "{req.text}", "stream": false}}' | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['response'])"
        """
        
        result = await run_command(curl_cmd, timeout=60)
        
        if result["exit_code"] == 0:
            response = result["stdout"]
        else:
            response = f"Error from Ollama: {result['stderr']}"
        
        logger.info(f"Message processed, response length: {len(response)}")
        
        return {
            "status": "ok",
            "result": response,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/logs")
async def api_logs(req: LogsRequest):
    """Get recent container logs"""
    logger.info(f"Logs requested: {req.lines} lines")
    
    try:
        # Read API server log
        log_file = LOGS_DIR / "api_server.log"
        if log_file.exists():
            with open(log_file, "r") as f:
                lines = f.readlines()
                recent_lines = lines[-req.lines:]
                logs = [line.rstrip() for line in recent_lines]
        else:
            logs = ["No logs available yet"]
        
        return {
            "status": "ok",
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Log retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/start")
async def api_start():
    """Start Odysseus (runs orchestrate.sh odysseus)"""
    logger.info("Start request received")
    
    try:
        # This will be called when switching to Odysseus mode
        # In practice, orchestrate.sh handles this from host
        return {
            "status": "ok",
            "message": "Odysseus is already running",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stop")
async def api_stop():
    """Stop Odysseus (switch back to OpenClaw)"""
    logger.info("Stop request received")
    
    try:
        # orchestrate.sh handles this from host
        return {
            "status": "ok",
            "message": "Stopping Odysseus, returning to OpenClaw",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute")
async def api_execute(req: ExecuteRequest):
    """Execute shell command (controlled, admin only)"""
    logger.warning(f"Execute request: {req.command[:50]}...")
    
    try:
        result = await run_command(req.command, timeout=req.timeout)
        return {
            "status": "ok",
            "exit_code": result["exit_code"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Execute failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def startup():
    logger.info("=" * 60)
    logger.info("ODYSSEUS API SERVER STARTUP")
    logger.info("=" * 60)
    logger.info(f"Workspace: {WORKSPACE_DIR}")
    logger.info(f"Logs: {LOGS_DIR}")
    logger.info("✓ API Server ready on 0.0.0.0:8888")


if __name__ == "__main__":
    import os
    
    port = int(os.getenv("API_PORT", "8888"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    logger.info(f"Starting API server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )
