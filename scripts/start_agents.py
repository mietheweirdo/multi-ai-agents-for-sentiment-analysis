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
    },
    {
        "name": "Conversational Agent",
        "script": "rpc_servers/conversational_agent_rpc.py",
        "port": os.getenv("CONVERSATIONAL_AGENT_PORT", "8010"),
        "env_var": "CONVERSATIONAL_AGENT_PORT"
    },
    {
        "name": "Enhanced A2A Coordinator",
        "script": "rpc_servers/enhanced_a2a_coordinator.py",
        "port": os.getenv("A2A_COORDINATOR_PORT", "8020"),
        "env_var": "A2A_COORDINATOR_PORT",
        "optional": True,
        "description": "True Agent-to-Agent communication coordinator"
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
    
    def start_agent(self, agent_config: Dict[str, str], force_start: bool = False) -> bool:
        """Start a single agent"""
        name = agent_config["name"]
        script = agent_config["script"]
        port = agent_config["port"]
        is_optional = agent_config.get("optional", False)
        
        # Skip optional agents unless forced
        if is_optional and not force_start:
            logger.info(f"⏭️  Skipping optional agent: {name} (use --a2a flag to enable)")
            return True
        
        # Check if port is available
        if not self.check_port_available(port):
            if is_optional:
                logger.warning(f"⚠️  Port {port} is already in use for optional {name}, skipping")
                return True
            else:
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
                if is_optional:
                    logger.info(f"🚀 {name} started successfully on port {port} (A2A enabled)")
                else:
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
                    logger.info(f" {name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f" {name} didn't stop gracefully, forcing...")
                    process.kill()
                    process.wait()
                    logger.info(f" {name} stopped forcefully")
                
            except Exception as e:
                logger.error(f" Error stopping {name}: {str(e)}")
            
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
    
    def start_all_agents(self, enable_a2a: bool = False) -> bool:
        """Start all agents"""
        logger.info("🚀 Starting multi-agent sentiment analysis system...")
        
        if enable_a2a:
            logger.info("🔗 A2A mode enabled - will start enhanced coordinator for true agent-to-agent communication")
            # Set environment variable for conversational agent
            os.environ["USE_A2A_COORDINATOR"] = "true"
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        success_count = 0
        total_agents = len(AGENTS)
        
        for agent_config in AGENTS:
            is_optional = agent_config.get("optional", False)
            
            if self.start_agent(agent_config, force_start=enable_a2a if is_optional else True):
                if not is_optional or enable_a2a:  # Count optional agents only if they actually started
                    success_count += 1
            else:
                if not is_optional:  # Only fail on required agents
                    logger.error(f"❌ Failed to start required agent: {agent_config['name']}")
                    return False
        
        # Calculate expected agents (required + optional if A2A enabled)
        required_agents = [a for a in AGENTS if not a.get("optional", False)]
        optional_agents = [a for a in AGENTS if a.get("optional", False)]
        
        expected_count = len(required_agents)
        if enable_a2a:
            expected_count += len(optional_agents)
        
        if success_count >= len(required_agents):
            if enable_a2a:
                logger.info(f"🎉 A2A system started! {success_count}/{expected_count} agents running")
                logger.info("🔗 Enhanced A2A coordinator enabled for true agent-to-agent communication")
            else:
                logger.info(f"✅ Standard system started! {success_count}/{len(required_agents)} agents running")
            
            self.running = True
            self.print_status(enable_a2a)
            return True
        else:
            logger.error(f"❌ System startup failed: {success_count}/{expected_count} agents started")
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
            logger.error(f" Missing required environment variables: {missing_vars}")
            logger.error("Please check your .env file")
            return False
        
        # Check OpenAI API key format
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key.startswith("sk-"):
            logger.warning(" OpenAI API key doesn't start with 'sk-', please verify")
        
        logger.info(" Environment validation passed")
        return True
    
    def print_status(self, a2a_enabled: bool = False):
        """Print status of all agents"""
        logger.info("\n" + "="*60)
        if a2a_enabled:
            logger.info("🔗 A2A MULTI-AGENT SYSTEM STATUS")
        else:
            logger.info("📊 SENTIMENT ANALYSIS AGENTS STATUS")
        logger.info("="*60)
        
        for agent_config in AGENTS:
            name = agent_config["name"]
            port = agent_config["port"]
            is_optional = agent_config.get("optional", False)
            
            if name in self.processes and self.processes[name].poll() is None:
                if is_optional and a2a_enabled:
                    status = "🚀 RUNNING (A2A)"
                elif is_optional:
                    status = "⏭️  SKIPPED (optional)"
                else:
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
                if is_optional and not a2a_enabled:
                    status = "⏭️  SKIPPED (optional)"
                else:
                    status = "🔴 STOPPED"
                logger.info(f"{name:<25} {status}")
                logger.info("")
        
        logger.info("="*60)
        logger.info("🚀 Usage:")
        logger.info("  - Start Chat Interface: streamlit run app.py")
        if a2a_enabled:
            logger.info("  - A2A Communication: Agents communicate via JSON-RPC")
            logger.info("  - Enhanced Coordinator: localhost:8020/health")
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
                            logger.warning(f" {name} has stopped unexpectedly, restarting...")
                            
                            # Remove the dead process
                            del self.processes[name]
                            
                            # Restart the agent
                            if self.start_agent(agent_config):
                                logger.info(f" {name} restarted successfully")
                            else:
                                logger.error(f" Failed to restart {name}")
                                
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
                    logger.info(f" {name} health check passed")
                else:
                    health_status[name] = False
                    logger.warning(f" {name} health check failed: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                health_status[name] = False
                logger.warning(f" {name} health check failed: {str(e)}")
        
        return health_status

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Multi-Agent Sentiment Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_agents.py                    # Start standard system
  python start_agents.py --a2a              # Start with A2A coordinator  
  python start_agents.py --a2a --no-monitor # A2A without monitoring
        """
    )
    parser.add_argument("--a2a", action="store_true", help="Enable A2A (Agent-to-Agent) communication mode")
    parser.add_argument("--no-monitor", action="store_true", help="Don't monitor agents after starting")
    parser.add_argument("--health-check", action="store_true", help="Perform health check only")
    parser.add_argument("--stop", action="store_true", help="Stop all running agents")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
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
    
    try:
        # Start all agents with A2A option
        if manager.start_all_agents(enable_a2a=args.a2a):
            if args.a2a:
                logger.info("🔗 A2A system ready! Agents communicate via JSON-RPC protocol")
            else:
                logger.info("✅ Standard system ready!")
            
            if not args.no_monitor:
                manager.monitor_agents()
            else:
                logger.info("💡 Agents started. Use --health-check to monitor or --stop to stop them.")
        else:
            logger.error("❌ Failed to start system")
            manager.stop_all_agents()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  Shutdown requested...")
        manager.stop_all_agents()
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        manager.stop_all_agents()
        sys.exit(1)

if __name__ == "__main__":
    main()
