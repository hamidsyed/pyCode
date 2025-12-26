def calculate_stairs(total_height, riser_height):
    """
    Calculate the number of steps and the riser height for stairs.
    
    Parameters:
    total_height (float): The total height of the stairs in inches.
    riser_height (float): The desired height of each riser in inches.
    
    Returns:
    int: The number of steps.
    float: The actual riser height.
    """
    # Calculate the number of steps
    num_steps = round(total_height / riser_height)
    
    # Calculate the actual riser height
    actual_riser_height = total_height / num_steps
    
    return num_steps, actual_riser_height

# Example usage
total_height = int(input("Enter Height: "))  # Total height of the stairs in inches
desired_riser_height = int(input("Riser height: "))  # Desired height of each riser in inches

num_steps, actual_riser_height = calculate_stairs(total_height, desired_riser_height)

print(f"Number of steps: {num_steps}")
print(f"Actual riser height: {actual_riser_height:.2f} inches")
