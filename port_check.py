import socket

def check_port(domain, ports=[80, 443], timeout=3):
    results = {}

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            result = sock.connect_ex((domain, port))

            if result == 0:
                results[port] = "open"
            else:
                results[port] = "closed"

            sock.close()

        except Exception as e:
            results[port] = f"error: {str(e)}"

    # if at least one port is open → server reachable
    is_alive = any(status == "open" for status in results.values())

    return {
        "status": is_alive,
        "ports": results
    }