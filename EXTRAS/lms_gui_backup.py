# THIS IS A BACKUP FILE(BASE GUI CODE) AND IS NOT TO BE USED FOR THE DEMONSTRATION OF THE GUI/CLIENT!!
# THIS IS A BACKUP FILE AND IS NOT TO BE USED FOR THE DEMONSTRATION OF THE GUI/CLIENT!!
# THIS IS A BACKUP FILE AND IS NOT TO BE USED FOR THE DEMONSTRATION OF THE GUI/CLIENT!!
# THIS IS A BACKUP FILE AND IS NOT TO BE USED FOR THE DEMONSTRATION OF THE GUI/CLIENT!!
# THIS IS A BACKUP FILE AND IS NOT TO BE USED FOR THE DEMONSTRATION OF THE GUI/CLIENT!!







import tkinter as tk
from tkinter import messagebox
import grpc
import lms_pb2
import lms_pb2_grpc
import os
from tkinter.filedialog import asksaveasfilename
from concurrent.futures import ThreadPoolExecutor  # For non-blocking GUI operations
import time




class LMSApp:

    def __init__(self, root):
     self.root = root
     self.root.title("LMS System")
     
     self.server_addresses = [
         '172.17.82.219:50051',  # Address of Server 1
         '172.18.18.44:50052',  # Address of Server 2
         '172.18.18.45:50053',  # Address of Server 3
         '172.18.18.50:50054',  # Address of Server 4
         '172.18.18.49:50055',  # Address of Server 5
     ]
 
     # Thread pool for async gRPC requests
     self.executor = ThreadPoolExecutor(max_workers=10)
     
     # Increase the max message size to 50MB
     MAX_MESSAGE_LENGTH = 50 * 1024 * 1024
 
     # Initialize leader address and gRPC channel dynamically (No hardcoded address)
     self.leader_address = None  # We will get the leader dynamically
     self.token = None
     self.role = None
 
     # Get the leader at the start
     try:
         self.leader_address = self.get_leader()
         self.channel = grpc.insecure_channel(
             self.leader_address,
             options=[
                 ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                 ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
             ]
         )
         self.stub = lms_pb2_grpc.LMSStub(self.channel)  # Initialize the stub with the leader
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to find a leader: {str(e)}")
 
     # Show login screen
     self.show_login()


    


    def get_leader(self):
     retry_attempts = 5  # Number of retries
     retry_delay = 3  # Seconds between retries
 
     # Iterate for a specified number of retry attempts
     for attempt in range(retry_attempts):
         for server in self.server_addresses:
             try:
                 print(f"Attempting to connect to server: {server}")
                 channel = grpc.insecure_channel(server)
                 stub = lms_pb2_grpc.RaftServiceStub(channel)
 
                 # Send a WhoIsLeader request to the current server
                 response = stub.WhoIsLeader(lms_pb2.Empty())

                 # Validate leader_id is within the range of server addresses
                 if 1 <= response.leader_id <= len(self.server_addresses):
 
                   # If the current server is the leader, return this server
                   if response.leader_id == self.server_addresses.index(server) + 1:
                       print(f"Leader found: Server {response.leader_id} is the leader.")
                       return server  # Return the leader's address
   
                   # If the server knows who the leader is, connect to that leader instead
                   elif response.leader_id != -1:
                       leader_address = self.server_addresses[response.leader_id - 1]
                       print(f"Redirecting to actual leader: Server {response.leader_id} at {leader_address}")
                       return leader_address
                   
                 else:
                     # Log invalid leader_id response and continue trying other servers
                     print(f"Invalid leader_id received: {response.leader_id}")
                     continue
 
             except grpc.RpcError as e:
                 print(f"Failed to communicate with server {server}: {e}")
                 continue  # Skip to the next server if this one fails

 
         # If no leader found, wait for the next retry attempt
         print(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
         time.sleep(retry_delay)
 
     # If no leader found after all retry attempts
     raise Exception("No leader found after multiple retries. Please ensure at least two servers are running.")



    def communicate_with_leader_async(self, action, *args):
     """Asynchronously communicate with the leader server."""
     retry_count = 0
     max_retries = 3
 
     # Detect the leader first
    #  if self.leader_address is None:
    #      self.leader_address = self.get_leader()

     self.leader_address = self.get_leader()  # Always fetch the current leader


     if self.leader_address is None:
            print("No leader found after checking all servers.")
            raise Exception("Failed to find leader after checking all servers.")
 
     while retry_count < max_retries:
         try:
             # Create a channel to the current leader
             channel = grpc.insecure_channel(self.leader_address)
             stub = lms_pb2_grpc.LMSStub(channel)
 
             # Perform the action asynchronously using a thread pool
             future = self.executor.submit(action, stub, *args)
             return future
 
         except grpc.RpcError as e:
             # If there is a communication error, retry with a new leader
             if e.code() in (
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.UNKNOWN,
            grpc.StatusCode.DEADLINE_EXCEEDED,
            grpc.StatusCode.CANCELLED,
            grpc.StatusCode.RESOURCE_EXHAUSTED  # Optional, in case of server overload
        ):
                 print(f"Leader at {self.leader_address} is unavailable. Retrying with a new leader...")
                 self.leader_address = self.get_leader()  # Find the new leader
                 retry_count += 1
                 continue  # Retry with the new leader
             else:
                 # Re-raise other gRPC errors
                 raise e
 
     raise Exception("Unable to communicate with leader after multiple attempts.")
    

    # to check leader before any operation
    # def execute_with_leader(self, action, *args):
    #  """Ensures the leader is detected before executing the action."""
    #  try:
    #      # Detect the current leader
    #      self.leader_address = self.get_leader()  # Update the leader's address
    #      self.channel = grpc.insecure_channel(self.leader_address)  # Reinitialize the gRPC channel with the leader
    #      self.stub = lms_pb2_grpc.LMSStub(self.channel)  # Update the stub for the leader
 
    #      # Execute the action (e.g., login or register)
    #      action(*args)
    #  except Exception as e:
    #      messagebox.showerror("Error", f"Failed to communicate with leader: {str(e)}")

    def execute_with_leader(self, action, *args):
     """Ensures the leader is detected before executing the action."""
     try:
         # Detect the current leader
         self.leader_address = self.get_leader()  # Update the leader's address
         self.channel = grpc.insecure_channel(self.leader_address)  # Reinitialize the gRPC channel with the leader
         self.stub = lms_pb2_grpc.LMSStub(self.channel)  # Create a new LMSStub using the leader channel
 
         # Now execute the action by passing the stub and any additional arguments
         return action(self.stub, *args)  # action expects the stub and other arguments to be passed
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to communicate with leader: {str(e)}")
         raise e  # Re-raise the exception for proper handling

 
 
 






    def show_login(self):
     """Login window for students and instructors"""
     self.clear_window()
 
     tk.Label(self.root, text="Username:").grid(row=0, column=0)
     self.username = tk.Entry(self.root)
     self.username.grid(row=0, column=1)
 
     tk.Label(self.root, text="Password:").grid(row=1, column=0)
     self.password = tk.Entry(self.root, show="*")
     self.password.grid(row=1, column=1)
 
     # Wrap login logic into a function that can accept the stub
     def login_with_stub(stub, *args):
         self.login()  # Call the login function without passing the stub directly
 
     # Modified login button to ensure leader detection before login
     tk.Button(self.root, text="Login", command=lambda: self.execute_with_leader(self.login)).grid(row=2, column=1)
 
     # Add a "Register" button to open the registration window
     tk.Button(self.root, text="Register", command=self.show_register).grid(row=3, column=1)


    def show_register(self):
     """Show the registration form"""
     self.clear_window()
 
     tk.Label(self.root, text="Register", font=("Arial", 16)).grid(row=0, column=1)
     
     tk.Label(self.root, text="Username:").grid(row=1, column=0)
     self.reg_username = tk.Entry(self.root)
     self.reg_username.grid(row=1, column=1)
 
     tk.Label(self.root, text="Password:").grid(row=2, column=0)
     self.reg_password = tk.Entry(self.root, show="*")
     self.reg_password.grid(row=2, column=1)
 
     tk.Label(self.root, text="Role:").grid(row=3, column=0)
     self.reg_role = tk.StringVar(value="student")
     tk.Radiobutton(self.root, text="Student", variable=self.reg_role, value="student").grid(row=3, column=1)
     tk.Radiobutton(self.root, text="Instructor", variable=self.reg_role, value="instructor").grid(row=3, column=2)
 
     # Modified register button to ensure leader detection before registering
     tk.Button(self.root, text="Register", command=lambda: self.execute_with_leader(self.register)).grid(row=4, column=1)
     tk.Button(self.root, text="Back to Login", command=self.show_login).grid(row=5, column=1)
 
 
    def register(self, stub):
     """Register a new user (student or instructor) asynchronously"""
     username = self.reg_username.get()
     password = self.reg_password.get()
     role = self.reg_role.get()
 
     def send_register_request(stub, *args):
         return stub.Register(lms_pb2.RegisterRequest(username=username, password=password, role=role))
 
     try:
         # Process the register request using the leader stub asynchronously
         future = self.communicate_with_leader_async(send_register_request)
         self.executor.submit(self.process_register_response, future)
 
     except grpc.RpcError as e:
         if e.code() == grpc.StatusCode.UNAVAILABLE:
             messagebox.showerror("Error", "Leader server is unavailable. Please try again later.")
         else:
             messagebox.showerror("Error", f"Failed to register: {str(e)}")



    def process_register_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Registration Success", response.message)
             self.show_login()  # Go back to login after successful registration
         else:
             messagebox.showerror("Registration Failed", response.message)
     except Exception as e:
         messagebox.showerror("Error", f"Failed to register: {str(e)}")
 

    def login(self, stub):
     """Handle user login asynchronously"""
     username = self.username.get()
     password = self.password.get()
 
     def send_login_request(stub, *args):
         return stub.Login(lms_pb2.LoginRequest(username=username, password=password))
 
     # Process the login request using the leader stub
     future = self.communicate_with_leader_async(send_login_request)
     self.executor.submit(self.process_login_response, future)

 
 

    def process_login_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             self.token = response.token
             self.role = response.role
 
             if self.role == "instructor":
                 self.show_instructor_menu()  # Show the instructor menu
             elif self.role == "student":
                 self.show_student_menu()  # Show the student menu
         else:
             messagebox.showerror("Error", "Login failed. Please check your credentials.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to login: {str(e)}")


    
    def clear_window(self):
        """Clear the current window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_student_menu(self):
     """Menu for students"""
     self.clear_window()
 
     tk.Label(self.root, text="Student Menu", font=("Arial", 16)).grid(row=0, column=1)
 
     # Ensure each button communicates with the correct leader
     tk.Button(self.root, text="View Course Material", command=lambda: self.execute_with_leader(self.view_course_material)).grid(row=1, column=1)
     tk.Button(self.root, text="Post Assignment", command=self.post_assignment).grid(row=2, column=1)
     tk.Button(self.root, text="View Grades", command=lambda: self.execute_with_leader(self.view_grades)).grid(row=3, column=1)
     tk.Button(self.root, text="Ask Query", command=self.ask_query).grid(row=4, column=1)
     tk.Button(self.root, text="View Instructor Responses", command=lambda: self.execute_with_leader(self.view_instructor_responses)).grid(row=5, column=1)
     tk.Button(self.root, text="Logout", command=lambda: self.execute_with_leader(self.logout)).grid(row=6, column=1)


    def show_instructor_menu(self):
     """Show instructor options."""
     self.clear_window()
 
     tk.Label(self.root, text="Instructor Menu", font=("Arial", 16)).grid(row=0, column=0)
 
     # Ensure each button communicates with the correct leader
     tk.Button(self.root, text="Post Course Material", command= self.post_course_material).grid(row=1, column=0)
     tk.Button(self.root, text="View and Grade Assignments", command= self.view_and_grade_assignments).grid(row=2, column=0)
     tk.Button(self.root, text="Respond to Query", command=lambda: self.execute_with_leader(self.respond_to_query)).grid(row=3, column=0)
     tk.Button(self.root, text="Logout", command=lambda: self.execute_with_leader(self.logout)).grid(row=4, column=0)
 


        #STUDENT OPTIONS

    def view_course_material(self, stub):
     """View and download course material posted by the instructor asynchronously."""
     self.clear_window()
 
     def get_course_material(stub, *args):
         return stub.Get(lms_pb2.GetRequest(token=self.token, type="course_material"))
 
     try:
         # Process the course material request asynchronously using the leader stub
         future = self.communicate_with_leader_async(get_course_material)
         
         # Submit the result to be processed when the future is done
         self.executor.submit(self.process_view_course_material_response, future)
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve course material: {str(e)}")




    def process_view_course_material_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             if not response.entries:  # If no entries exist, check message
                 messagebox.showinfo("Course Material", response.message)
                 self.show_student_menu()  # Go back to the student menu if no materials are available
                 return  # Exit early if no entries
 
             row = 1  # Track row for dynamic UI layout
             for entry in response.entries:
                 instructor_name = entry.instructor if hasattr(entry, 'instructor') else "Unknown"
                 # Display instructor name and course material filename
                 tk.Label(self.root, text=f"Instructor: {instructor_name}, File: {entry.filename}").grid(row=row, column=0)
 
                 # Button to download the course material
                 tk.Button(self.root, text="Download", command=lambda e=entry: self.download_course_material(e)).grid(row=row, column=1)
                 row += 1  # Increment row for next course material
 
             tk.Button(self.root, text="Go Back", command=self.show_student_menu).grid(row=row, column=0)
         else:
             messagebox.showerror("Error", "Failed to retrieve course material.")
             self.show_student_menu()
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve course material: {str(e)}")
         self.show_student_menu()
 

    def download_course_material(self, entry):
     """Download course material and ask where to save it."""
     save_path = asksaveasfilename(defaultextension=".pdf", initialfile=entry.filename, 
                                   title="Save Course Material", 
                                   filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
 
     if save_path:
         try:
             def download_course_material_data(stub, *args):
                 return stub.Get(lms_pb2.GetRequest(token=self.token, type="course_material"))
 
             # Make asynchronous call to download the course material
             future = self.communicate_with_leader_async(download_course_material_data)
 
             # Submit the future for processing the response and saving the file
             self.executor.submit(self.process_download_course_material_response, future, save_path)
 
         except Exception as e:
             messagebox.showerror("Error", f"Failed to save course material: {str(e)}")



    def process_download_course_material_response(self, future, save_path):
     try:
         response = future.result()  # Wait for the result
         if response.success and response.entries:
             with open(save_path, 'wb') as f:
                 f.write(response.entries[0].file)  # Write the file content to the chosen location
             messagebox.showinfo("Success", f"Course material saved to {save_path}")
         else:
             messagebox.showerror("Error", "Failed to download course material.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to save course material: {str(e)}")
 


    def post_assignment(self):
     """Post assignment by selecting a file"""
     self.clear_window()
 
     tk.Label(self.root, text="Enter the file path:").grid(row=0, column=0)
     self.file_path = tk.Entry(self.root)
     self.file_path.grid(row=0, column=1)
     tk.Button(self.root, text="Submit", command=lambda: self.execute_with_leader(self.submit_assignment)).grid(row=1, column=1)
     # Add the "Go Back" button
     tk.Button(self.root, text="Go Back", command=self.go_back).grid(row=2, column=1)


    def submit_assignment(self, stub):
     """Submit assignment by posting the file to the leader server."""
     file_path = self.file_path.get()
 
     try:
         # Read the assignment file
         with open(file_path, 'rb') as f:
             file_data = f.read()
         filename = os.path.basename(file_path)
 
         def post_assignment(stub, *args):
             return stub.Post(lms_pb2.PostRequest(token=self.token, type="assignment", file=file_data, filename=filename))
 
         # Post the assignment asynchronously using the leader stub
         future = self.communicate_with_leader_async(post_assignment)
 
         # Submit the future to the executor for asynchronous handling
         self.executor.submit(self.process_submit_assignment_response, future)
 
     except FileNotFoundError:
         messagebox.showerror("Error", "File not found.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to post assignment: {str(e)}")



    def process_submit_assignment_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Success", "Assignment posted successfully.")
         else:
             messagebox.showerror("Error", "Failed to post assignment.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to post assignment: {str(e)}")


    def view_grades(self, stub):
     """View grades asynchronously."""
     def get_grades(stub, *args):
         return stub.GetGrade(lms_pb2.GetGradeRequest(token=self.token))
 
     try:
         # Send the asynchronous request to get grades
         future = self.communicate_with_leader_async(get_grades)
         
         # Submit the future to the executor for handling the response asynchronously
         self.executor.submit(self.process_view_grades_response, future)
     
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve grades: {str(e)}")
 


    def process_view_grades_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             if response.grade == "No grades available yet." or response.grade == "Grade not yet assigned":
                 messagebox.showinfo("Grades", response.grade)
                 return  # Do not clear the window if just showing a dialog
             else:
                 self.clear_window()
                 tk.Label(self.root, text="Your Grades", font=("Arial", 16)).grid(row=0, column=1)
                 tk.Label(self.root, text=response.grade).grid(row=1, column=1)
 
                 # Add "Go Back" button
                 tk.Button(self.root, text="Go Back", command=self.go_back).grid(row=2, column=1)
         else:
             messagebox.showerror("Error", "Failed to retrieve grades.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve grades: {str(e)}")




    def ask_query(self):
     """UI for students to ask a query to the instructor or LLM"""
     self.clear_window()
 
     tk.Label(self.root, text="Enter your query:").grid(row=0, column=0)
     self.query_text = tk.Entry(self.root)
     self.query_text.grid(row=0, column=1)
 
     tk.Label(self.root, text="Ask from Instructor or LLM?").grid(row=1, column=0)
     self.query_option = tk.StringVar(value="llm")
     tk.Radiobutton(self.root, text="Instructor", variable=self.query_option, value="instructor").grid(row=1, column=1)
     tk.Radiobutton(self.root, text="LLM", variable=self.query_option, value="llm").grid(row=1, column=2)
 
     tk.Button(self.root, text="Submit Query", command=lambda: self.execute_with_leader(self.submit_query)).grid(row=3, column=1)

 
     # Add "Go Back" button
     tk.Button(self.root, text="Go Back", command=self.go_back).grid(row=4, column=1)


    def submit_query(self, stub):
     """Send query to instructor or LLM based on user's choice asynchronously."""
     query = self.query_text.get()
     option = self.query_option.get()
 
     try:
         if option == "llm":
             def send_llm_query(stub, *args):
                 return stub.GetLLMAnswer(lms_pb2.QueryRequest(token=self.token, query=query))
 
             # Send the query to LLM asynchronously using the leader stub
             future = self.communicate_with_leader_async(send_llm_query)
             self.executor.submit(self.process_llm_query_response, future)
 
         elif option == "instructor":
             def send_instructor_query(stub, *args):
                 return stub.Post(lms_pb2.PostRequest(token=self.token, type="query", data=query))
 
             # Send the query to the instructor asynchronously using the leader stub
             future = self.communicate_with_leader_async(send_instructor_query)
             self.executor.submit(self.process_instructor_query_response, future)
     
     except Exception as e:
         messagebox.showerror("Error", f"Failed to submit query: {str(e)}")
 
 

    def process_llm_query_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("LLM Response", response.response)
         else:
             messagebox.showerror("Error", "Failed to retrieve answer from LLM.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve LLM answer: {str(e)}")
 

    def process_instructor_query_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Success", "Query sent to the instructor successfully.")
         else:
             messagebox.showerror("Error", "Failed to send query to the instructor.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to send query: {str(e)}")





    def view_instructor_responses(self, stub):
     """Student view for instructor's responses to their queries asynchronously."""
     self.clear_window()
 
     def get_instructor_responses(stub, *args):
         return stub.GetInstructorResponse(lms_pb2.GetRequest(token=self.token))
 
     try:
         # Send the request to get instructor responses asynchronously using the leader stub
         future = self.communicate_with_leader_async(get_instructor_responses)
         
         # Submit the future to the executor for handling the response asynchronously
         self.executor.submit(self.process_instructor_responses_response, future)
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve instructor responses: {str(e)}")
 


    def process_instructor_responses_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             if not response.entries:
                 messagebox.showinfo("Responses", "No instructor responses available.")
                 self.show_student_menu()
                 return  # Do not clear the window if just showing a dialog
 
             # Display the responses
             for entry in response.entries:
                 tk.Label(self.root, text=entry.data).pack()
 
             # Add "Go Back" button
             tk.Button(self.root, text="Go Back", command=self.go_back).pack()
         else:
             messagebox.showerror("Error", "Failed to retrieve responses.")
             self.show_student_menu()
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve responses: {str(e)}")
         self.show_student_menu()





    def go_back(self):
     """Go back to the student or instructor menu depending on the role"""
     if self.role == "student":
        self.show_student_menu()
     else:
        self.show_instructor_menu()



        #INSTRUCTOR OPTIONS


    #left
    def post_course_material(self):
     self.clear_window()
 
     tk.Label(self.root, text="Post Course Material", font=("Arial", 16)).grid(row=0, column=1)
 
     tk.Label(self.root, text="Enter the file path:").grid(row=1, column=0)
     self.file_path = tk.Entry(self.root)
     self.file_path.grid(row=1, column=1)
 
     tk.Button(self.root, text="Submit", command=lambda: self.execute_with_leader(self.submit_course_material)).grid(row=2, column=1)
 
     # Add "Go Back" button
     tk.Button(self.root, text="Go Back", command=self.go_back).grid(row=3, column=1)



    def submit_course_material(self, stub):
     """Submit course material asynchronously by posting the file to the leader server."""
     file_path = self.file_path.get()
 
     try:
         # Read the course material file
         with open(file_path, 'rb') as f:
             file_data = f.read()
         filename = os.path.basename(file_path)
 
         def post_course_material(stub, *args):
             return stub.Post(lms_pb2.PostRequest(token=self.token, type="course_material", file=file_data, filename=filename))
 
         # Post the course material asynchronously using the leader stub
         future = self.communicate_with_leader_async(post_course_material)
 
         # Submit the future to the executor for asynchronous handling
         self.executor.submit(self.process_submit_course_material_response, future)
 
     except FileNotFoundError:
         messagebox.showerror("Error", "File not found.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to post course material: {str(e)}")



    def process_submit_course_material_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Success", "Course material posted successfully.")
         else:
             messagebox.showerror("Error", "Failed to post course material.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to post course material: {str(e)}")


    def view_and_grade_assignments(self):
     """Instructor view to download assignments and grade students asynchronously."""
     self.clear_window()
 
     def get_student_assignments(stub, *args):
         return stub.Get(lms_pb2.GetRequest(token=self.token, type="student_list"))
 
     try:
         # Send the request to get student assignments asynchronously using the leader stub
         future = self.communicate_with_leader_async(get_student_assignments)
 
         # Submit the future to the executor for processing the response
         self.executor.submit(self.process_view_and_grade_assignments_response, future)
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve assignments: {str(e)}")



    def process_view_and_grade_assignments_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             if not response.entries:
                 messagebox.showinfo("Student List", "No assignments left to grade.")
                 self.show_instructor_menu()  # Go back to the instructor menu if no assignments are available
                 return  # Exit early if no entries
 
             row = 1  # Track row for dynamic UI layout
             for entry in response.entries:
                 # Display student ID and assignment name
                 tk.Label(self.root, text=f"Assignment from Student ID: {entry.id}, File: {entry.filename}").grid(row=row, column=0)
 
                 # Button to download the assignment
                 tk.Button(self.root, text="Download Assignment", command=lambda e=entry: self.execute_with_leader(lambda stub: self.download_assignment(stub, e))).grid(row=row, column=1)

 
                 # Field to enter the grade
                 tk.Label(self.root, text="Enter Grade:").grid(row=row, column=2)
                 grade_entry = tk.Entry(self.root)
                 grade_entry.grid(row=row, column=3)
 
                 # Button to submit the grade
                 tk.Button(self.root, text="Submit Grade", command=lambda e=entry, g=grade_entry: self.execute_with_leader(lambda stub: self.submit_grade(stub, e, g))).grid(row=row, column=4)

 
                 row += 1  # Increment row for next student assignment
 
             # Add "Go Back" button
             tk.Button(self.root, text="Go Back", command=self.show_instructor_menu).grid(row=row, column=1)
 
         else:
             messagebox.showerror("Error", "Failed to retrieve student list.")
             self.show_instructor_menu()
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve student list: {str(e)}")
         self.show_instructor_menu()
 


    def download_assignment(self, stub, entry):
     """Download assignment file and ask where to save it."""
     save_path = asksaveasfilename(defaultextension=".pdf", initialfile=entry.filename, 
                                   title="Save Assignment", 
                                   filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
 
     if save_path:
         try:
             def download_assignment_data(stub, *args):
                 return stub.Get(lms_pb2.GetRequest(token=self.token, type="student_list"))
 
             # Send the request asynchronously to download the assignment using the leader stub
             future = self.communicate_with_leader_async(download_assignment_data)
 
             # Submit the future to the executor for processing the response asynchronously
             self.executor.submit(self.process_download_assignment_response, future, save_path)
 
         except Exception as e:
             messagebox.showerror("Error", f"Failed to save assignment: {str(e)}")



    def process_download_assignment_response(self, future, save_path):
     try:
         response = future.result()  # Wait for the result
         if response.success and response.entries:
             with open(save_path, 'wb') as f:
                 f.write(response.entries[0].file)  # Write the file content to the chosen location
             messagebox.showinfo("Success", f"Assignment saved to {save_path}")
         else:
             messagebox.showerror("Error", "Failed to download the assignment.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to save assignment: {str(e)}")


    def submit_grade(self, stub, entry, grade_entry):
     """Submit the grade for the student's assignment asynchronously."""
     grade = grade_entry.get()
     if not grade:
         messagebox.showerror("Error", "Please enter a grade before submitting.")
         return
 
     def submit_grade_request(stub, *args):
         return stub.GradeAssignment(lms_pb2.GradeRequest(token=self.token, studentId=entry.id, grade=grade))
 
     try:
         # Send the request asynchronously to submit the grade using the leader stub
         future = self.communicate_with_leader_async(submit_grade_request)
 
         # Submit the future to the executor for processing the response asynchronously
         self.executor.submit(self.process_submit_grade_response, future, entry.id, grade)
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to submit grade: {str(e)}")

 
 
    def process_submit_grade_response(self, future, student_id, grade):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Success", f"Grade {grade} submitted for Student ID: {student_id}")
 
             # After grading, refresh the assignment list
             self.view_and_grade_assignments()
         else:
             messagebox.showerror("Error", "Failed to submit grade.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to submit grade: {str(e)}")






    def respond_to_query(self, stub):
     """UI for instructor to respond to student queries asynchronously."""
     self.clear_window()
 
     def get_unanswered_queries(stub, *args):
         return stub.GetUnansweredQueries(lms_pb2.GetRequest(token=self.token))
 
     try:
         # Send the request asynchronously to get unanswered queries using the leader stub
         future = self.communicate_with_leader_async(get_unanswered_queries)
 
         # Submit the future to the executor for processing the response asynchronously
         self.executor.submit(self.process_respond_to_query_response, future)
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve unanswered queries: {str(e)}")



    def process_respond_to_query_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             if not response.entries:
                 messagebox.showinfo("Respond to Queries", "No unanswered queries.")
                 self.show_instructor_menu()  # Go back to the instructor menu if no queries are available
                 return  # Return early to avoid displaying a blank screen
 
             # Create a dictionary where the key is the student ID and query, and the value is just the query
             self.student_queries = {f"{entry.id}: {entry.data}": entry.id for entry in response.entries}
 
             # Display queries in a dropdown
             self.selected_query = tk.StringVar(self.root)
             self.selected_query.set(list(self.student_queries.keys())[0])  # Set the first query as the default
 
             tk.Label(self.root, text="Select Query to Respond").grid(row=1, column=0)
             tk.OptionMenu(self.root, self.selected_query, *self.student_queries.keys()).grid(row=1, column=1)
 
             tk.Label(self.root, text="Enter Response").grid(row=2, column=0)
             self.query_response = tk.Entry(self.root)
             self.query_response.grid(row=2, column=1)
 
             tk.Button(self.root, text="Submit Response", command=lambda: self.execute_with_leader(self.submit_response)).grid(row=3, column=1)

 
             # Add "Go Back" button
             tk.Button(self.root, text="Go Back", command=self.show_instructor_menu).grid(row=4, column=1)
 
         else:
             messagebox.showerror("Error", "Failed to retrieve queries.")
             self.show_instructor_menu()  # Return to the instructor menu if there's an error
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to retrieve queries: {str(e)}")
         self.show_instructor_menu()


    def submit_response(self, stub):
     """Submit instructor's response to the selected query asynchronously."""
     # Get the selected query (which includes both student ID and query text)
     selected_query_key = self.selected_query.get()
 
     # Extract the student ID from the selected query (it's stored in self.student_queries)
     student_id = self.student_queries[selected_query_key]
 
     # Get the instructor's response
     response_text = self.query_response.get()
 
     def submit_instructor_response(stub, *args):
         return stub.RespondToQuery(lms_pb2.PostRequest(token=self.token, studentId=student_id, data=response_text))
 
     try:
         # Send the request asynchronously to submit the instructor's response using the leader stub
         future = self.communicate_with_leader_async(submit_instructor_response)
 
         # Submit the future to the executor for processing the response asynchronously
         self.executor.submit(self.process_submit_response_response, future)
 
     except Exception as e:
         messagebox.showerror("Error", f"Failed to send response: {str(e)}")



    def process_submit_response_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Success", "Response sent successfully.")
             self.show_instructor_menu()  # Go back to the instructor menu after submitting the response
         else:
             messagebox.showerror("Error", "Failed to send response.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to send response: {str(e)}")
 
 





    def logout(self, stub):
     """Handle user logout with leader re-election in case the leader is down."""
     def send_logout_request(stub, *args):
         return stub.Logout(lms_pb2.LogoutRequest(token=self.token))
 
     try:
         # Process the logout request using the leader stub asynchronously
         future = self.communicate_with_leader_async(send_logout_request)
         self.executor.submit(self.process_logout_response, future)
 
     except grpc.RpcError as e:
         if e.code() == grpc.StatusCode.UNAVAILABLE:
             messagebox.showerror("Error", "Leader server is unavailable. Trying to find the new leader...")
             try:
                 # Attempt to find a new leader and retry logout
                 self.get_leader()  # Refresh leader detection
                 future = self.communicate_with_leader_async(send_logout_request)
                 self.executor.submit(self.process_logout_response, future)
             except Exception as e:
                 messagebox.showerror("Error", f"Failed to log out after retrying: {str(e)}")
         else:
             messagebox.showerror("Error", f"Failed to log out: {str(e)}")


    def process_logout_response(self, future):
     try:
         response = future.result()  # Wait for the result
         if response.success:
             messagebox.showinfo("Logout", "Logged out successfully.")
             self.token = None
             self.role = None
             self.show_login()  # Show login after successful logout
         else:
             messagebox.showerror("Error", "Failed to log out.")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to log out: {str(e)}")
 
 

if __name__ == "__main__":
    root = tk.Tk()
    app = LMSApp(root)
    root.mainloop()