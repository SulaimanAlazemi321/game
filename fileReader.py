from colorama import Fore, Style

with open(r"D:\Downloads\item_data_1.txt") as f:
    for line in f:
        if line.startswith("/") or line.startswith("\n"):
            continue
        title, refrenceNumber, price, id, available = line.split(",")
        status = f"{Fore.GREEN}available{Style.RESET_ALL}" if available.strip().lower() == "true" else f"{Fore.RED}not available{Style.RESET_ALL}"
        print(
            f"the title is: {Fore.GREEN}{title}{Style.RESET_ALL}, with a reference number of {Fore.GREEN}{refrenceNumber}{Style.RESET_ALL} "
            f"that has price of: {Fore.GREEN}{price}{Style.RESET_ALL} which its ID is: {Fore.GREEN}{id}{Style.RESET_ALL} and it is: {status}"
        )
