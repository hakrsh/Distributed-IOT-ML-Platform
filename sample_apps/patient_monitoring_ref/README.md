# Patient monitoring model
## Endpoints
* /vitals-checker:
  * POST:
    * json:
        * spo2:
            * type: float
        * pulserate
            * type: float
        * temperature
            * type: float
    * response:
        * status:
            * type: int
            * example: 200
        * body:
            * type: string
            * "Safe" or "Critical"
    * description:
        * "This endpoint is used to check the patient's vital signs."
* /diabetes-checker:
  * POST:
    * json:
        * glucose:
            * type: float
        * insulin
            * type: float
        * bmi
            * type: float
        * age
            * type: int
    * response:
        * status:
            * type: int
            * example: 200
        * body:
            * type: string
            * "true" or "false"
    * description:
        * "This endpoint is used to check the patient's diabetes."
