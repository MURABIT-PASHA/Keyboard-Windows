# QR Code Networking App

This application serves as a networking tool that displays a QR code for connecting devices over a network. It runs in the background with a system tray icon on Windows, allowing for easy access and minimal disruption to the user's workflow.

## Features

- Generates a QR code that represents the local IP address of the host machine.
- Listens for incoming connections on a specified port.
- Processes incoming messages to perform actions such as typing text or executing commands.

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.6 or later
- PyQt5
- qrcode
- pynput (for keyboard interactions)
- pyperclip (for clipboard interactions)

You can install the necessary Python packages using pip:

```bash
pip install PyQt5 qrcode pynput pyperclip
```
## Running the Application

1. **Clone or download this repository** to your local machine.

2. **Navigate to the application directory** in your terminal or command prompt.

3. **Run the application** by executing the Python script:

    ```bash
    python app.py
    ```

## Usage

- Upon running, the application will minimize to the system tray.
- Click the system tray icon and select **"Bağla"** to display the QR code.
- Scan the QR code with a device to obtain the IP address of the host machine.
- Use the provided IP address to establish a connection from another device.

## Exiting the Application

- Right-click the system tray icon and select **"Çıkış"** to close the application.

## Customization

- You can modify the `PORT` variable in the script to use a different port for listening to incoming connections.
- The QR code generation and the actions performed upon receiving messages can be customized in the `process_message` function.

## Known Issues

- The application currently does not authenticate incoming connections. It's recommended to use this tool in a secure and trusted network environment.

## Future Improvements

- Implement authentication for establishing connections.
- Enhance the user interface for better usability.
- Add support for more complex commands and interactions.

## License

This project is open-source and available under the MIT License.
