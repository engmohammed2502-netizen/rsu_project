# rsu_project

## Project Overview
**Zero the Engineer's Library** is a robust, self-hosted Learning Management System (LMS) and digital repository designed specifically for the Faculty of Engineering at Red Sea University. The platform bridges the gap between digital accessibility and infrastructure constraints by offering a **Hybrid Access Model**: accessible via the campus Local Area Network (LAN) for offline connectivity and the Wide Area Network (WAN) for remote access.

This project demonstrates a full-cycle implementation, from backend development with **Django** to containerized deployment on a **Linux-based Home Lab**.

##  Architecture & Tech Stack
* **Application Logic:** Django (Python) providing a secure and scalable backend.
* **Containerization:** Docker & Docker Compose for microservices orchestration (App Service + Database Service).
* **Database:** MariaDB/PostgreSQL (Containerized).
* **Web Server/Reverse Proxy:** Nginx Proxy Manager / Web Server handling request routing.
* **Infrastructure:**
    * **Host:** Ubuntu Server 22.04 LTS running on VMware Workstation (Bridge Mode).
    * **Hardware:** Local Home Lab (i7 8th Gen, Allocated Virtual Resources).
* **Networking:** Custom NAT configuration, Port Forwarding, and DNS management for hybrid LAN/WAN availability.

## Key Features
* **Role-Based Access Control (RBAC):**
    * **Root/Superuser:** Full system control and log monitoring.
    * **Professors:** CRUD operations for course materials and student management (Freeze/Unfreeze accounts).
    * **Students:** Access to materials and subject-specific discussion forums.
    * **Guests:** Read-only access to public resources.
* **Interactive Forums:** Subject-specific discussion boards for peer-to-peer support.
* **Centralized Resource Management:** Upload/Download capabilties for lectures, assignments, and exams.

##  Deployment & Operations
The system is deployed using a containerized strategy on a virtualization layer:
* **Environment:** Virtualized Ubuntu Server instance utilizing strict resource allocation (4GB RAM, 20GB Storage).
* **Log Analysis:** Proactive monitoring of container logs to troubleshoot connection refuse errors and database latency.
* **Security:** Network-level security via firewall configuration, port management, and user session handling.
