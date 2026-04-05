# Implementation Plan

## Product Overview
**LostLink** is a web application that helps students and university staff report and browse lost and found items on campus.

The product includes three required components:
- **Backend** — processes requests, applies business logic, and connects the frontend with the database.
- **Database** — stores lost and found item reports.
- **End-user-facing client** — a web interface for creating and browsing reports.

## Version 1
### Goal
Build one core feature well: allow users to submit a lost or found item report and see it in the public list.

### Why this feature
This is the most valuable and easiest feature to implement because it directly solves the main user problem: there is no single place to report and view lost and found items on campus.

### Functionality
Version 1 includes:
- a web form to submit a lost or found item report;
- backend logic to receive and validate the submitted data;
- database storage for item reports;
- a page that displays all submitted reports.

### Expected Result
A working web application where users can create a report and browse the list of reports. This version is functional and ready to be shown to the TA for feedback.

## Version 2
### Goal
Improve Version 1 by adding usability features, addressing TA feedback, and preparing the product for deployment.

### Functionality
Version 2 includes:
- filtering by item type (**lost** / **found**);
- filtering by item status (**open** / **resolved**);
- item details page;
- ability to mark an item as resolved;
- improved frontend design and validation;
- fixes and improvements based on TA feedback;
- Dockerized deployment on a VM.

### Expected Result
A more polished and deployable version of the product that extends the core functionality of Version 1 and is accessible online.

## Development Approach
The project is developed incrementally:
1. implement Version 1;
2. test it and show it to the TA;
3. collect TA feedback;
4. implement Version 2 improvements;
5. Dockerize the services;
6. deploy the product on a VM.

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Deployment:** Docker, Docker Compose, Ubuntu 24.04 VM
