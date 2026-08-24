stock_data = {}

try:
    with open('stock.txt', 'r') as file:
       for line_num,line in enumerate(file,1):
           line = line.strip()
           if not line:
               continue
           parts = line.split(',')
           if len(parts) != 2:
              raise ValueError
           item, quantity = parts[0].strip(), parts[1].strip()
           stock_data[item] = int(quantity)
    print(stock_data)      
except FileNotFoundError:
    print("Stock file not found.")          
except ValueError:
    print(f"Error: Invalid format in the file at line {line_num}. Each line must contain an item and a quantity separated by a comma.")


def show_stock():
    if not stock_data:
        print("Stock is empty.")
    else:
        for index, (item, quantity) in enumerate(stock_data.items(), 1):
                print(f"{index}. {item}: {quantity}") 
                        
def add_item():
    show_stock()
    added_item = input("Enter the item to add: ")
    added_item = added_item.lower()
    if added_item.isdigit() and 1 <= int(added_item) <= len(stock_data):
        added_item = list(stock_data.keys())[int(added_item) - 1]
    while True:
        raw_qty = input("Enter the quantity to add: ")
        if raw_qty.isdigit():
            added_quantity = int(raw_qty)
            break
        print("Please enter a valid number.")
    
    if added_item in stock_data or added_item in stock_data.keys():
        stock_data[added_item] += added_quantity
    else:
        stock_data[added_item] = added_quantity
def remove_item():
    show_stock()
    removed_item = input("Enter the item to remove: ")
    removed_item = removed_item.lower()
    if removed_item.isdigit() and 1 <= int(removed_item) <= len(stock_data):
        removed_item = list(stock_data.keys())[int(removed_item) - 1]
    while True:
        raw_qty = input("Enter the quantity to remove: ")
        if raw_qty.isdigit():
            removed_quantity = int(raw_qty)
            break
        print("Please enter a valid number.")
    
    if removed_item in stock_data:
        if stock_data[removed_item] >= removed_quantity:
            stock_data[removed_item] -= removed_quantity
            if stock_data[removed_item] == 0:
                del stock_data[removed_item]
        elif stock_data[removed_item] < removed_quantity:
            print(f"Error: Not enough quantity of {removed_item} to remove.")
    else:
        print(f"Error: {removed_item} not found in stock.")
def save_changes():
    with open('stock.txt', 'w') as file:
        for item, quantity in stock_data.items():
            file.write(f"{item},{quantity}\n") 
select = 0
while select != 4:
    print("1. Add stock")
    print("2. Remove stock")
    print("3. Show stock's content")
    print("4. Exit the program")
    select = int(input("Select an option: "))
    if select == 1:
        add_item()
    elif select == 2:
        remove_item()
    elif select == 3:
        show_stock()
    elif select == 4:
        save_changes()
        print("Exiting the program....")
        exit()
    else:
        print("Invalid option. Please try again.")
