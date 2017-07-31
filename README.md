# bl-status-api - EMS Box Loading System - REST API
The purpose of this repository is the manage the code and documentation for the **RESTful API** component of the Box Loading Status (bl-status) System

## Overview
The Box Loading Status system **API** provides an interface for external apps to submit CRUD requests against the system's underlying Database (MongoDB).  The RESTful API uses HTTP protocol to communicate with external apps.  The **C**reate, **R**ead, **U**pdate, and **Delete** opertaions (CRUD) are mapped to the corresponding http verbs (POST, GET, PUT, DELETE), respectively.  Django and the Django REST API Framework (Python based) will be used to build out the API.
