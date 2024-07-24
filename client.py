import socket
import pickle

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

### SERVER FUNCTIONS ###
def send_request(client_socket, request, data=None):
    try:
        client_socket.send(request.encode())
        if data:
            client_socket.send(data)
        response = client_socket.recv(1024)
        return response
    except socket.timeout:
        print("Socket operation timed out.")
        return None

def get_menu(client_socket):
    response = send_request(client_socket, 'GET_MENU')
    if response:
        menu = pickle.loads(response)
        return menu
    return None

def update_menu(client_socket, updated_menu):
    serialized_menu = pickle.dumps(updated_menu)
    response = send_request(client_socket, 'UPDATE_MENU', serialized_menu)
    if response:
        print("Response:", response.decode())
    else:
        print("Failed to update menu.")

def checkout_cart(client_socket, cart):
    serialized_cart = pickle.dumps(cart)
    response = send_request(client_socket, 'CHECKOUT_CART', serialized_cart)
    if response:
        print("Response:", response.decode())
    else:
        print("Failed to checkout cart.")

def authenticate(client_socket, username, password):
    credentials = f"{username}\n{password}"
    response = send_request(client_socket, 'LOGIN', credentials.encode())
    if response:
        logged_user = pickle.loads(response)
        return logged_user
    return None

### CLIENT FUNCTIONS ###
def pressEnter():
    input("Press Enter to continue...")

def y_n_input(prompt):
    while True:
        value = input(prompt)
        if value.lower() in ['yes', 'no', 'y', 'n', 'true', 'false']:
            return value
        print("Invalid input. Please enter 'yes' or 'no'.")
        
def update_int_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")
            
def update_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def update_str_input(prompt):
    while True:
        value = input(prompt)
        if value:
            return value
        print("Invalid input. Please enter a value.")    
        
def print_menu(menu):
    for i,item in enumerate(menu, 1):
        print(f"{i}. {item['item']}: ${item['price']} - Quantity: {item['quantity']}")

def add_to_cart(item, quantity, cart):
    if item in cart:
        cart[item] += quantity
    else:
        cart[item] = quantity

def display_cart(cart):
    print("Cart:")
    for item, quantity in cart.items():
        print(f"{item}: {quantity}")

def remove_from_cart(item, cart):
    if item in cart:
        del cart[item]
        print(f"{item} removed from cart.")
    else:
        print(f"{item} not found in cart.")

def calculate_total(cart, menu):
    total = 0
    for item, quantity in cart.items():
        for menu_item in menu:
            if menu_item['item'] == item:
                total += menu_item['price'] * quantity
                break
    return total

def buy_items(client_socket, cart, menu):
    total = calculate_total(cart, menu)
    print("Final Order Summary:")
    display_cart(cart)
    print(f"Total: ${total}")
    if y_n_input("Confirm order? (yes/no): ") in ['yes', 'y', 'true']:
        print("Order confirmed.")
        # Send order to server
        checkout_cart(client_socket, cart)
        pass
    else:
        print("Order cancelled.")


### MENU FUNCTIONS ###
def showAdminMenu():
    print("1. Update Menu")
    print("2. Place Order")
    print("3. Checkout Cart")
    print("4. Exit")
    return input("Enter choice: ")

def showCustomerMenu():
    print("1. View Menu")
    print("2. Checkout Cart")
    print("3. Exit")
    return input("Enter choice: ")

def adminMenu(client_socket):
    cart = {}
    while True:
        print("\033[H\033[J")
        print("Admin Menu")
        choice = showAdminMenu()
        if choice == '1':
            print("Update Menu")
            menu = get_menu(client_socket)
            if menu:
                print("Current Menu:")
                print_menu(menu)
                item_number = update_int_input("Enter item number to update: ")
                if item_number < 1 or item_number > len(menu):
                    print("Invalid item number. Please try again.")
                    pressEnter()
                    continue
                print(f"Item: {menu[item_number-1]['item']}")
                
                if y_n_input("Do you want to update this item? (yes/no): ") in ['no', 'n', 'false']:
                    continue
                name = update_str_input(f"Enter new item name: ")
                price = update_float_input("Enter new price: ")
                quantity = update_int_input("Enter new quantity: ")
                menu[item_number-1].update({'item': name})
                menu[item_number-1].update({'price': price})
                menu[item_number-1].update({'quantity': quantity})
                print("Updated Menu:")
                update_menu(client_socket, menu)
            pressEnter()
        elif choice == '2':
            print("Place Order")
            print("Menu:")
            menu = get_menu(client_socket)
            if menu:
                print_menu(menu)
                # add to cart
                item_number = update_int_input("Enter item number to add to cart: ")
                if item_number < 1 or item_number > len(menu):
                    print("Invalid item number. Please try again.")
                    pressEnter()
                    continue
                print(f"Item: {menu[item_number-1]['item']}")
                quantity = update_int_input("Enter quantity: ")
                if quantity < 1 or quantity > menu[item_number-1]['quantity']:
                    print("Invalid quantity. Please try again.")
                    pressEnter()
                    continue
                
                add_to_cart(menu[item_number-1]['item'], quantity, cart)
            pressEnter()
        elif choice == '3':
            if cart:
                buy_items(client_socket, cart, menu)
                cart.clear()
            else:
                print("Your cart is empty.")
            pressEnter()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Try again.")

def customerMenu(client_socket):
    cart = {}
    while True:
        print("\033[H\033[J")
        print("Customer Menu")
        choice = showCustomerMenu()
        if choice == '1':
            print("Menu:")
            menu = get_menu(client_socket)
            if menu:
                print_menu(menu)
                
                # add to cart
                item_number = update_int_input("Enter item number to add to cart: ")
                if item_number < 1 or item_number > len(menu):
                    print("Invalid item number. Please try again.")
                    pressEnter()
                    continue
                print(f"Item: {menu[item_number-1]['item']}")
                quantity = update_int_input("Enter quantity: ")
                if quantity < 1 or quantity > menu[item_number-1]['quantity']:
                    print("Invalid quantity. Please try again.")
                    pressEnter()
                    continue
                
                add_to_cart(menu[item_number-1]['item'], quantity, cart)
                
                pressEnter()
        elif choice == '2':
            if cart:
                buy_items(client_socket, cart, menu)
                cart.clear()
            else:
                print("Your cart is empty.")
            pressEnter()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")

### MAIN FUNCTION ###
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10.0) # Set a timeout of 10 seconds

    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("\033[H\033[J")
        print("Welcome to the Restaurant Management System")
        print("We are connected to server.")
        print("Login")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        logged_user = authenticate(client_socket, username, password)
        
        print(logged_user)
        
        if not logged_user:
            print("Authentication failed. Exiting...")
            return
        
        if logged_user['role'] == 'owner':
            adminMenu(client_socket)
        elif logged_user['role'] == 'customer':
            customerMenu(client_socket)
        else:
            print("Invalid role. Exiting...")
            return

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
