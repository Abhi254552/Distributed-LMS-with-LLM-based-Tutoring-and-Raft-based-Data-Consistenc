================================================================================
                LEARNING MANAGEMENT SYSTEM (LMS) - MILESTONE 3
================================================================================

This updated version of the Learning Management System (LMS) now incorporates the 
RAFT consensus protocol for distributed data consistency across five servers. The 
system, built using Python, gRPC, and Tkinter for the GUI, allows students and 
instructors to interact through functionalities such as assignments, grades, 
course materials, and an LLM-based query system. The RAFT protocol ensures high 
availability and fault tolerance by synchronizing data across servers.


--------------------------------------------------------------------------------
                                PREREQUISITES
--------------------------------------------------------------------------------

Before running the LMS system, ensure the following are installed:

1. Python 3.9 or higher

2. Required Libraries:
   - grpcio
   - grpcio-tools
   - tkinter (usually included with Python)
   - transformers
   - protobuf
   - PyPDF2
   - torch

   You can install these dependencies with the following command:

   pip install grpcio grpcio-tools transformers protobuf PyPDF2 torch


--------------------------------------------------------------------------------
                              STEPS TO RUN THE PROGRAM
--------------------------------------------------------------------------------

1. Generate gRPC Code from the Proto File
   -----------------------------------------------------------
   *Optional if `lms_pb2.py` and `lms_pb2_grpc.py` are already 
   present*

   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. lms.proto


2. Run the LMS Servers
   -----------------------------------------------------------
   Each server should run on a different computer to demonstrate 
   RAFT-based data consistency. Below are the commands to be 
   used on five different machines:
   
   *************************
   (If you want to run and test all the servers and client yourself then search for 
    '#EDIT THE IP ADDRESSES BELOW' 
    in the lms_gui_final.py and lms_server.py files. And change the addresses of the server you will run your servers
    and tutoring server on)
   *************************

      Server 1:
      python lms_server.py 1 50051 172.18.18.44:50052 172.18.18.45:50053 172.18.18.50:50054 172.18.18.49:50055

      Server 2:
      python lms_server.py 2 50052 172.17.82.219:50051 172.18.18.45:50053 172.18.18.50:50054 172.18.18.49:50055

      Server 3:
      python lms_server.py 3 50053 172.17.82.219:50051 172.18.18.44:50052 172.18.18.50:50054 172.18.18.49:50055

      Server 4:
      python lms_server.py 4 50054 172.17.82.219:50051 172.18.18.44:50052 172.18.18.45:50053 172.18.18.49:50055

      Server 5:
      python lms_server.py 5 50055 172.17.82.219:50051 172.18.18.44:50052 172.18.18.45:50053 172.18.18.50:50054


3. Run the Tutoring Server
   -----------------------------------------------------------
   In another terminal, navigate to the folder containing `tutoring_server.py` 
   and run it on a separate computer:

      python tutoring_server.py


4. Run the GUI Client
   -----------------------------------------------------------
   Finally, run the GUI client on another machine to interact with the LMS system. 
   The client will connect to the RAFT leader for handling requests:

      python lms_gui_final.py


--------------------------------------------------------------------------------
                                   NOTES
--------------------------------------------------------------------------------

- Leader Detection: The client connects only to the leader server for performing 
  operations. If the leader changes due to RAFT protocol, the client will reconnect 
  to the new leader.
  
- Data Consistency: RAFT ensures data consistency across all servers by replicating 
  logs and committing data to follower servers.

- Troubleshooting:
    - Connection Refused: Verify that each server machine has opened the specified 
      ports for external access and that no firewall blocks are preventing 
      communication.


================================================================================
                            END OF INSTRUCTIONS
================================================================================
