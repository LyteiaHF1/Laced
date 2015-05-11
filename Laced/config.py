from paypal import PayPalConfig
from paypal import PayPalInterface

config = PayPalConfig(API_USERNAME = "highfashionentertainment_api1.gmail.com",
                      API_PASSWORD = "MFGC8D9DE8PBKBEY",
                      API_SIGNATURE = "AiPC9BjkCyDFQXbSkoZcgqH3hpacA5ZWYR-yj3kHGF7DagKtHVEKYCxY",
                      DEBUG_LEVEL=0)

interface = PayPalInterface(config=config)
