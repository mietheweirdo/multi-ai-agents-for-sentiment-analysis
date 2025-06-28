# scripts/start_agents.py
"""
Startup script for all A2A sentiment analysis agents
Starts all RPC servers concurrently following A2A Cross-Framework POC pattern
"""

import os
import sys
import subprocess
import time
import signal
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agent configurations
AGENTS = [
    {
        "name": "Quality Agent",
        "script": "rpc_servers/quality_agent_rpc.py",
        "port": os.getenv("QUALITY_AGENT_PORT", "8001"),
        "env_var": "QUALITY_AGENT_PORT"
    },
    {
        "name": "Experience Agent", 
        "script": "rpc_servers/experience_agent_rpc.py",
        "port": os.getenv("EXPERIENCE_AGENT_PORT", "8002"),
        "env_var": "EXPERIENCE_AGENT_PORT"
    },
    {
        "name": "User Experience Agent",
        "script": "rpc_servers/user_experience_agent_rpc.py", 
        "port": os.getenv("USER_EXPERIENCE_AGENT_PORT", "8003"),
        "env_var": "USER_EXPERIENCE_AGENT_PORT"
    },
    {
        "name": "Business Agent",
        "script": "rpc_servers/business_agent_rpc.py",
        "port": os.getenv("BUSINESS_AGENT_PORT", "8004"),
        "env_var": "BUSINESS_AGENT_PORT"
    },
    {
        "name": "Technical Agent",
        "script": "rpc_servers/technical_agent_rpc.py",
        "port": os.getenv("TECHNICAL_AGENT_PORT", "8005"),
        "env_var": "TECHNICAL_AGENT_PORT"
    },
    {
        "name": "Coordinator Agent",
        "script": "rpc_servers/coordinator_agent_rpc.py",
        "port": os.getenv("COORDINATOR_AGENT_PORT", "8000"),
        "env_var": "COORDINATOR_AGENT_PORT"
    }
]

class AgentManager:
    """Manages starting, stopping, and monitoring of A2A sentiment analysis agents"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down agents...")
        self.stop_all_agents()
        sys.exit(0)
    
    def check_port_available(self, port: str) -> bool:
        """Check if a port is available"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', int(port)))
                return True
        except OSError:
            return False
    
    def start_agent(self, agent_config: Dict[str, str]) -> bool:
        """Start a single agent"""
        name = agent_config["name"]
        script = agent_config["script"]
        port = agent_config["port"]
        
        # Check if port is available
        if not self.check_port_available(port):
            logger.error(f"Port {port} is already in use for {name}")
            return False
        
        # Check if script exists
        if not os.path.exists(script):
            logger.error(f"Script not found: {script}")
            return False
        
        logger.info(f"Starting {name} on port {port}...")
        
        try:
            # Start the agent process
            process = subprocess.Popen(
                [sys.executable, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[name] = process
            
            # Give the process a moment to start
            time.sleep(1)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ {name} started successfully on port {port}")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {name} failed to start:")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {str(e)}")
            return False
    
    def stop_agent(self, name: str):
        """Stop a single agent"""
        if name in self.processes:
            process = self.processes[name]
            logger.info(f"Stopping {name}...")
            
            try:
                process.terminate()
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    process.wait(timeout=5)
                    logger.info(f"✅ {name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ {name} didn't stop gracefully, forcing...")
                    process.kill()
                    process.wait()
                    logger.info(f"✅ {name} stopped forcefully")
                
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {str(e)}")
            
            finally:
                del self.processes[name]
    
    def stop_all_agents(self):
        """Stop all running agents"""
        logger.info("Stopping all agents...")
        
        agent_names = list(self.processes.keys())
        for name in agent_names:
            self.stop_agent(name)
        
        self.running = False
        logger.info("All agents stopped")
    
    def start_all_agents(self) -> bool:
        """Start all agents"""
        logger.info("Starting all A2A sentiment analysis agents...")
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        success_count = 0
        
        for agent_config in AGENTS:
            if self.start_agent(agent_config):
                success_count += 1
            else:
                logger.error(f"Failed to start {agent_config['name']}")
        
        if success_count == len(AGENTS):
            logger.info(f"🎉 All {len(AGENTS)} agents started successfully!")
            self.running = True
            self.print_status()
            return True
        else:
            logger.error(f"⚠️ Only {success_count}/{len(AGENTS)} agents started successfully")
            return False
    
    def validate_environment(self) -> bool:
        """Validate environment configuration"""
        logger.info("Validating environment configuration...")
        
        # Check required environment variables
        required_vars = ["OPENAI_API_KEY", "OPENAI_MODEL"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.error("Please check your .env file")
            return False
        
        # Check OpenAI API key format
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key.startswith("sk-"):
            logger.warning("⚠️ OpenAI API key doesn't start with 'sk-', please verify")
        
        logger.info("✅ Environment validation passed")
        return True
    
    def print_status(self):
        """Print status of all agents"""
        logger.info("\n" + "="*60)
        logger.info("🤖 A2A SENTIMENT ANALYSIS AGENTS STATUS")
        logger.info("="*60)
        
        for agent_config in AGENTS:
            name = agent_config["name"]
            port = agent_config["port"]
            
            if name in self.processes and self.processes[name].poll() is None:
                status = "🟢 RUNNING"
                url = f"http://localhost:{port}"
                rpc_url = f"http://localhost:{port}/rpc"
                health_url = f"http://localhost:{port}/health"
                card_url = f"http://localhost:{port}/.well-known/agent.json"
                
                logger.info(f"{name:<25} {status}")
                logger.info(f"  Port: {port}")
                logger.info(f"  RPC: {rpc_url}")
                logger.info(f"  Health: {health_url}")
                logger.info(f"  Card: {card_url}")
                logger.info("")
            else:
                status = "🔴 STOPPED"
                logger.info(f"{name:<25} {status}")
                logger.info("")
        
        logger.info("="*60)
        logger.info("💡 Usage:")
        logger.info("  - Start Streamlit UI: streamlit run app.py")
        logger.info("  - Test RPC endpoints with curl or Postman")
        logger.info("  - View agent cards at /.well-known/agent.json")
        logger.info("  - Check health at /health")
        logger.info("="*60)
    
    def monitor_agents(self):
        """Monitor running agents and restart if they crash"""
        logger.info("Monitoring agents... Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(5)  # Check every 5 seconds
                
                for agent_config in AGENTS:
                    name = agent_config["name"]
                    
                    if name in self.processes:
                        process = self.processes[name]
                        
                        # Check if process is still running
                        if process.poll() is not None:
                            logger.warning(f"⚠️ {name} has stopped unexpectedly, restarting...")
                            
                            # Remove the dead process
                            del self.processes[name]
                            
                            # Restart the agent
                            if self.start_agent(agent_config):
                                logger.info(f"✅ {name} restarted successfully")
                            else:
                                logger.error(f"❌ Failed to restart {name}")
                                
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
    
    def health_check(self) -> Dict[str, bool]:
        """Perform health check on all agents"""
        import requests
        
        logger.info("Performing health check...")
        health_status = {}
        
        for agent_config in AGENTS:
            name = agent_config["name"]
            port = agent_config["port"]
            health_url = f"http://localhost:{port}/health"
            
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    health_status[name] = True
                    logger.info(f"✅ {name} health check passed")
                else:
                    health_status[name] = False
                    logger.warning(f"⚠️ {name} health check failed: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                health_status[name] = False
                logger.warning(f"⚠️ {name} health check failed: {str(e)}")
        
        return health_status

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="A2A Sentiment Analysis Agent Manager")
    parser.add_argument("--no-monitor", action="store_true", help="Don't monitor agents after starting")
    parser.add_argument("--health-check", action="store_true", help="Perform health check only")
    parser.add_argument("--stop", action="store_true", help="Stop all running agents")
    
    args = parser.parse_args()
    
    manager = AgentManager()
    
    if args.health_check:
        health_status = manager.health_check()
        healthy_count = sum(health_status.values())
        total_count = len(health_status)
        logger.info(f"Health check complete: {healthy_count}/{total_count} agents healthy")
        sys.exit(0 if healthy_count == total_count else 1)
    
    if args.stop:
        manager.stop_all_agents()
        sys.exit(0)
    
    # Start all agents
    if manager.start_all_agents():
        if not args.no_monitor:
            manager.monitor_agents()
        else:
            logger.info("Agents started. Use --health-check to monitor or --stop to stop them.")
    else:
        logger.error("Failed to start all agents")
        manager.stop_all_agents()
        sys.exit(1)

if __name__ == "__main__":
    main()
