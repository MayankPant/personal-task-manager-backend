def capitalize(input: str) -> str:
    try:
        return " ".join([input[0].upper() + input[1:] for input in input.split(" ")])
    except Exception as e:
        print(f"Error Occured: {e}")
        return ""