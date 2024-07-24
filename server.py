import socket
import pickle

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
MENU_FILE = 'menu.pickle'
USER_FILE = 'users.pickle'

def load_menu():
    try:
        with open(MENU_FILE, 'rb') as f:
            menu = pickle.load(f)
            if not isinstance(menu, list):
                print("Invalid menu file format. Creating a new menu file.")
                menu = {}
    except (FileNotFoundError, pickle.UnpicklingError):
        print("Menu file not found or corrupted. Creating a new menu file.")
        menu = {}
    return menu

def load_users():
    try:
        with open(USER_FILE, 'rb') as f:
            users = pickle.load(f)
            if not isinstance(users, list):
                print("Invalid users file format. Creating a new users file.")
                users = {}
    except (FileNotFoundError, pickle.UnpicklingError):
        print("Users file not found or corrupted. Creating a new users file.")
        users = {}
    return users

def save_menu(menu):
    with open(MENU_FILE, 'wb') as f:
        pickle.dump(menu, f)

def auth_user(users, username, password):
    logged_user = None
    for user in users:
        if user['username'] == username and user['password'] == password:
            logged_user = user
            break
    
    if not logged_user:
        print("User not found or invalid credentials.")
        return None
    
    return logged_user

authenticated_user = False
def handle_client_connection(client_socket):
    menu = load_menu()
    users = load_users()

    while True:
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
        except ConnectionAbortedError:
            print("Connection closed by the client.")
            break
        except UnicodeDecodeError as e:
            print("UnicodeDecodeError:", e)
            continue  # Continue to the next iteration of the loop

        if request == 'GET_MENU':
            client_socket.send(pickle.dumps(menu))
        
        elif request == 'UPDATE_MENU':
            if authenticated_user["role"] == 'owner':
                try:
                    updated_menu_data = client_socket.recv(1024)
                    updated_menu = pickle.loads(updated_menu_data)
                    menu = updated_menu
                    save_menu(menu)
                    client_socket.send(b'Menu updated successfully')
                except pickle.UnpicklingError as e:
                    print("Error unpickling updated menu data:", e)  # Debugging
                    client_socket.send(b'Error updating menu')
                except Exception as e:
                    print("Error updating menu:", e)  # Debugging
                    client_socket.send(b'Error updating menu')
            else:
                client_socket.send(b'Menu update failed: Authentication required')  # Corrected response
        
        elif request == 'CHECKOUT_CART':
            if authenticated_user["role"] == 'customer' or authenticated_user["role"] == 'owner':
                cart_data = client_socket.recv(1024)
                cart = pickle.loads(cart_data)
                # deduct the quantity of items in the cart from the menu
                for item in cart.keys():
                    for menu_item in menu:
                        if menu_item['item'] == item:
                            if menu_item['quantity'] < cart[item]:
                                client_socket.send(b'Cart checkout failed: Insufficient quantity')
                                break
                            menu_item['quantity'] -= cart[item]
                            client_socket.send(b'Cart checked out successfully')
                            break
                save_menu(menu)
            else:
                client_socket.send(b'Cart checkout failed: Authentication required')
        elif request == 'LOGIN':
            print("Received LOGIN request")
            credentials = client_socket.recv(1024).decode('utf-8').split('\n')
            username = credentials[0]
            password = credentials[1]
            authenticated_user = auth_user(users, username, password)
            if authenticated_user is not None:
                print("Authentication successful")
                client_socket.send(pickle.dumps(authenticated_user))
            else:
                print("Authentication failed")
                client_socket.send(b'Authentication failed')
        
    client_socket.close()



def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} established.")
        handle_client_connection(client_socket)

    server_socket.close()

if __name__ == "__main__":
    main()
