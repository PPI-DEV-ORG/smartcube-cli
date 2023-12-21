# SmartCube CLI Module

**Note:**
- This module is programmed in Python 3.10.12.
- Currently, it is compatible with Linux systems only.

## Running SmartCube CLI

SmartCube CLI can be executed in two ways: manually or by utilizing the program installer available at [SmartCube Installer](https://github.com/PPI-Capstone-Project/smartcube-installer).

### Manual Execution:

1. Clone the repository:
    ```bash
    git clone https://github.com/PPI-Capstone-Project/multiprocessing_video_source_modul.git
    ```

2. Set up dependencies:
    ```bash
    pip install 
    cd multiprocessing_video_source_modul
    source bin/activate
    pip install -r requirements.txt
    ```

3. Set Up Environment Variable:
    - Create a new file named `.env`:
        ```bash
        touch .env
        nano .env
        ```

    - Paste the following variables:
        ```env
        # SMARTCUBE_API_URL=http://localhost:3000

        EDGE_ACCESS_TOKEN=your_edge_token

        BREAK_TIME_WHEN_OBJECT_DETECTED=15

        MQTT_HOST="f1096f5d.ala.asia-southeast1.emqxsl.com"
        MQTT_PORT="8883"
        MQTT_CA_CERT="mqtt-ssl.crt"
        MQTT_USERNAME="zoc"
        MQTT_PASSWORD="zocc"
        MQTT_PUB_TOPIC=your_publisher_topic
        MQTT_SUB_TOPIC=your_subscriber_topic
        ```

4. Place `mqtt-ssl.crt` inside the project folder. You can request `mqtt-ssl.crt` via email at c550bky4408@bangkit.academy.

5. Run the application:
    ```bash
    python app.py
    ```

For detailed installation instructions, please refer to the [SmartCube Installer](https://github.com/PPI-Capstone-Project/smartcube-installer) link.
