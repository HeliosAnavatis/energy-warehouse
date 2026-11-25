class HomeAssistantCollector:

    def __init__(self, client, tank_top, tank_bottom):
        self.client = client
        self.tank_top = tank_top
        self.tank_bottom = tank_bottom

    def get_tank_temperatures(self):

        top = self.client.get_state(
            self.tank_top
        )

        bottom = self.client.get_state(
            self.tank_bottom
        )

        return {
            "top": float(top["state"]),
            "bottom": float(bottom["state"]),
        }