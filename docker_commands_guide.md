# Docker Commands Guide - Sidemen ETL Project

This guide contains all the Docker commands we used to set up and run the Sidemen YouTube ETL pipeline.

## 🐳 Basic Docker Commands

### **Check Running Containers**
```bash
docker ps
```
**What it does:** Shows all currently running containers with their status, ports, and names.

### **Check All Containers (Including Stopped)**
```bash
docker ps -a
```
**What it does:** Shows all containers (running and stopped) with their full status.

### **Check Container Resources**
```bash
docker stats
```
**What it does:** Shows real-time resource usage (CPU, memory, network) of running containers.

### **Check Container Resources (One-time)**
```bash
docker stats --no-stream
```
**What it does:** Shows resource usage once and exits (doesn't keep updating).

---

## 🚀 Docker Compose Commands

### **Start All Services**
```bash
docker-compose up -d
```
**What it does:** 
- Starts all services defined in `docker-compose.yaml`
- `-d` means "detached" (runs in background)
- Creates containers for Airflow, MongoDB, PostgreSQL

### **Start Specific Service**
```bash
docker-compose up mongo -d
```
**What it does:** Starts only the MongoDB service in the background.

### **Start Multiple Services**
```bash
docker-compose up airflow-webserver airflow-scheduler -d
```
**What it does:** Starts only Airflow webserver and scheduler services.

### **Stop All Services**
```bash
docker-compose down
```
**What it does:** Stops and removes all containers, but keeps volumes (data).

### **Stop and Remove Everything**
```bash
docker-compose down -v
```
**What it does:** Stops containers AND removes volumes (deletes all data).

### **Restart All Services**
```bash
docker-compose restart
```
**What it does:** Restarts all running containers without recreating them.

### **Restart Specific Service**
```bash
docker-compose restart airflow-webserver
```
**What it does:** Restarts only the Airflow webserver container.

### **Check Service Status**
```bash
docker-compose ps
```
**What it does:** Shows status of all services defined in docker-compose.yaml.

---

## 📋 Container Management

### **Stop a Specific Container**
```bash
docker stop sidemenproject-airflow-webserver-1
```
**What it does:** Stops the Airflow webserver container by name.

### **Start a Stopped Container**
```bash
docker start sidemenproject-airflow-webserver-1
```
**What it does:** Starts a previously stopped container.

### **Remove a Container**
```bash
docker rm sidemenproject-airflow-webserver-1
```
**What it does:** Removes a stopped container (deletes it permanently).

### **Stop All Running Containers**
```bash
docker stop $(docker ps -q)
```
**What it does:** Stops all currently running containers.

---

## 🔍 Logs and Debugging

### **View Service Logs**
```bash
docker-compose logs airflow-webserver
```
**What it does:** Shows logs from the Airflow webserver service.

### **View Recent Logs**
```bash
docker-compose logs --tail=50 airflow-webserver
```
**What it does:** Shows only the last 50 lines of logs.

### **View All Service Logs**
```bash
docker-compose logs
```
**What it does:** Shows logs from all services.

### **Follow Logs in Real-time**
```bash
docker-compose logs -f airflow-webserver
```
**What it does:** Shows logs and continues to show new logs as they appear.

---

## 🗄️ Database Commands

### **Connect to MongoDB**
```bash
docker exec -it sidemenproject-mongo-1 mongosh
```
**What it does:** Opens MongoDB shell inside the MongoDB container.

### **Run MongoDB Command**
```bash
docker exec -it sidemenproject-mongo-1 mongosh --eval "use Sidemen; db.sidemen_stats.countDocuments()"
```
**What it does:** Runs a MongoDB command and shows the result.

### **Check MongoDB Health**
```bash
docker exec -it sidemenproject-mongo-1 mongosh --eval "db.runCommand('ping')"
```
**What it does:** Tests if MongoDB is responding properly.

---

## 🔧 Airflow Commands

### **Initialize Airflow Database**
```bash
docker-compose run --rm airflow-webserver airflow db init
```
**What it does:** Creates and initializes the Airflow metadata database.

### **Create Airflow User**
```bash
docker-compose run --rm airflow-webserver airflow users create --role Admin --username admin --email admin@example.com --firstname admin --lastname admin --password admin
```
**What it does:** Creates a new admin user for Airflow web interface.

### **Delete Airflow User**
```bash
docker-compose run --rm airflow-webserver airflow users delete --username admin
```
**What it does:** Removes a user from Airflow.

### **Run Airflow CLI**
```bash
docker-compose run --rm airflow-cli airflow
```
**What it does:** Opens Airflow command-line interface.

---

## 🏗️ Building and Running

### **Build Docker Image**
```bash
docker build -t sidemen-etl .
```
**What it does:** Builds a Docker image from your Dockerfile with the name "sidemen-etl".

### **Run Container**
```bash
docker run --rm sidemen-etl
```
**What it does:** Runs the sidemen-etl container and removes it when done.

### **Run Container with Network**
```bash
docker run --rm --network sidemenproject_default sidemen-etl
```
**What it does:** Runs container and connects it to the project's Docker network.

### **Run Container with Environment Variables**
```bash
docker run --rm -e MONGO_URI=mongodb://sidemenproject-mongo-1:27017/ sidemen-etl
```
**What it does:** Runs container with custom MongoDB URI.

---

## 🌐 Network Commands

### **List Docker Networks**
```bash
docker network ls
```
**What it does:** Shows all Docker networks (bridge, host, custom networks).

### **Inspect Network**
```bash
docker inspect sidemenproject-mongo-1
```
**What it does:** Shows detailed information about a container, including its network settings.

---

## 🧹 Cleanup Commands

### **Remove Unused Images**
```bash
docker image prune
```
**What it does:** Removes unused Docker images to free up space.

### **Remove Everything Unused**
```bash
docker system prune -f
```
**What it does:** Removes all unused containers, networks, images (use `-f` to skip confirmation).

### **Remove Everything Including Volumes**
```bash
docker system prune -a --volumes
```
**What it does:** Removes everything unused including volumes (WARNING: deletes all data).

---

## 📊 Monitoring Commands

### **Check Container Health**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
**What it does:** Shows containers in a nice table format with status and ports.

### **Check Disk Usage**
```bash
docker system df
```
**What it does:** Shows how much disk space Docker is using.

---

## 🚨 Troubleshooting Commands

### **Check if Port is in Use**
```bash
netstat -ano | findstr :8081
```
**What it does:** Shows if port 8081 is being used by another process (Windows).

### **Kill Process Using Port**
```bash
taskkill /PID <PID> /F
```
**What it does:** Kills a process by its Process ID (replace <PID> with actual number).

---

## 📝 Common Workflows

### **Complete Reset (When things go wrong)**
```bash
# Stop everything
docker-compose down

# Remove all unused resources
docker system prune -f

# Start fresh
docker-compose up -d
```

### **Check if Everything is Working**
```bash
# Check all containers are running
docker ps

# Check Airflow is accessible
curl http://localhost:8081

# Check MongoDB is working
docker exec -it sidemenproject-mongo-1 mongosh --eval "db.runCommand('ping')"
```

### **Daily Operations**
```bash
# Start everything
docker-compose up -d

# Check status
docker ps

# View logs if needed
docker-compose logs airflow-webserver

# Stop when done
docker-compose down
```

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `docker ps` | See running containers |
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose logs` | View logs |
| `docker exec -it container-name command` | Run command in container |
| `docker-compose restart` | Restart all services |

---

**Remember:** Always use `docker-compose` commands when working with your project, as they manage multiple containers together! 