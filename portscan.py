try:
    from scapy.all import IP, TCP, sr1
    import sys

    target_ip = None
    port_range = None

    args = " ".join(sys.argv[1:]).replace(" ", "")
    for argument in args.split("-"):
        if "=" in argument:
            key, value = argument.split("=", 1)
            if key == 'ip':
                target_ip = value
            elif key == 'ports':
                port_range = value  

    if not port_range or not target_ip:
        print(f"Please enter:\n{sys.argv[0]} -ip=<TargetIP> -ports=<start-end>")
        sys.exit()

  

    open_ports = []
    closed_ports = []

    for port in range(int(port_range)): 
        packet = IP(dst=target_ip)/TCP(dport=port, flags='S')
        response = sr1(packet, verbose=0, timeout=1)

        if response and response.haslayer(TCP):
            if response[TCP].flags == 0x12:
                open_ports.append(port)
                print(f"Open port: {port}")


    print(f"Open ports: {open_ports}")

except KeyboardInterrupt:
    print("Exiting..")
except Exception as e:
    print(f"Error: {e}")
