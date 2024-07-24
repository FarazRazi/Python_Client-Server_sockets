import pickle

# Define the menu dictionary
menu = [
    {
        'item': 'Pizza',
        'price': 10.99,
        'quantity': 5
    },
    {
        'item': 'Burger',
        'price': 8.49,
        'quantity': 2
    },
    {
        'item': 'Salad',
        'price': 6.99,
        'quantity': 3
    },
    {
        'item': 'Fries',
        'price': 3.49,
        'quantity': 6
    },
    {
        'item': 'Soda',
        'price': 1.99,
        'quantity': 10
    }
]

users = [
    {
        'username': 'admin',
        'password': 'admin',
        'role': 'owner'
    },
    {
        'username': 'user1',
        'password': 'pass1',
        'role': 'customer'
    },
    {
        'username': 'user2',
        'password': 'pass2',
        'role': 'customer'
    }
]

# Save the menu dictionary to the menu.pickle file
with open('menu.pickle', 'wb') as f:
    pickle.dump(menu, f)
    
with open('users.pickle', 'wb') as f:
    pickle.dump(users, f)

print("Menu file created successfully.")
print("Customers file created successfully.")
