import argon2
from argon2 import Type

# Initialize the Argon2 Password Hasher with Type.ID, matching the app's settings
ph = argon2.PasswordHasher(type=Type.ID)

def main():
    print("String Hashing Tool (Type 'exit' to quit)\n")
    
    while True:
        # Prompt the developer for a string to hash
        user_input = input("Enter a string to hash: ")
        
        if user_input.lower() == 'exit':
            print("Exiting the hashing tool.")
            break
        
        # Hash the input and display the hashed result
        try:
            hashed_password = ph.hash(user_input)
            print(f"Hashed value: {hashed_password}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
