import pandas as pd

voltage_mapping = {
    "0": 0,  # Policy 0.9: Line with voltage 0 means that's internal line between two adjacent substations
    "69/72": 69,
    "138/144": 138,
    "240": 240,
    "500": 500,
}


class DataLoader:
    def __init__(self):
        # Load DataFrame
        self.lines_df = pd.read_csv("..\\data\\Line.csv")
        self.points_df = pd.read_csv("..\\data\\Substation.csv")

        self.points_df['substation'] = self.points_df['substation'].astype(str).str.replace("\n", " ", regex=False)

        self.cities_df = pd.read_csv("..\\data\\CityPopulationPoint.csv")
        self.city_population_df = pd.read_csv(
            "..\\data\\Population City Distribution.csv")  # Data Source: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001101
        self.planning_area_border_df = pd.read_csv("..\\data\\PlanningAreaBorder.csv")
        self.city_border_df = pd.read_csv("..\\data\\CityBorder.csv")
        self.line_voltage_df = pd.read_csv("..\\data\\LineVoltage.csv")
        self.generator_substation_df = pd.read_csv("..\\data\\GeneratorSubstation.csv")

        self.city_population_df["Population, 2016"] = (
            self.city_population_df["Population, 2016"]
            .astype(str)
            .str.replace("r", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )
        self.city_population_df["Land area in square kilometres, 2021"] = self.city_population_df[
            "Land area in square kilometres, 2021"].astype(float)

        # Utility Data Structures
        self.city_to_population = {}
        self.city_to_coordinates = {}

        self.substations_to_coordinates = {}
        self.coordinates_to_substations = {}

        self.lines_to_station_pairs = {}
        self.stations_to_lines = {}
        self.undirect_station_pairs_to_line = {}
        self.direct_station_pairs_to_line = {}

        self.generators_to_substations = {}
        self.generators_to_capacities = {}
        self.substations_to_generators = {}

        self.lines_to_voltage = {}
        self.substations_to_voltage = {}

        self.planning_area_border_edges = []

        self.planning_area_border_df[["Start_X", "End_X", "Start_Y", "End_Y"]] *= 1000
        self.city_border_df[["Start_X", "End_X", "Start_Y", "End_Y"]] *= 1000
        self.lines_df[["Start_X", "End_X", "Start_Y", "End_Y"]] *= 1000
        self.cities_df[["x", "y"]] *= 1000
        self.points_df[["x", "y"]] *= 1000

        self.initialize_city()
        self.initialize_coordinates()  # Initialize the coordinates of lines and substations

        self.initialize_line_station_relationships()  # Initialize the line-station relationships
        self.initialize_generator_mappings()  # Initialize the generator information
        self.initialize_network_voltage()  # Initialize the network voltage information

        self.initialize_border()  # Initialize the border information

        # for start, end in self.undirect_station_pairs_to_line.keys():
        #     if (start, end) not in self.direct_station_pairs_to_line and (end, start) not in self.direct_station_pairs_to_line:
        #         self.direct_station_pairs_to_line[(start, end)] = False

        # Define the constants
        self.planning_area_gen_area_dict = {
            1: "17", 2: "18", 3: "19", 4: "25", 5: "21", 6: "34", 7: "22", 8: "29", 9: "44", 10: "53", 11: "55",
            12: "20",
            13: "23", 14: "24", 15: "26", 16: "40", 17: "27", 18: "28", 19: "33", 20: "56", 21: "60", 22: "31",
            23: "30",
            24: "38", 25: "35", 26: "39", 27: "42", 28: "36", 29: "57", 30: "6", 31: "46", 32: "49", 33: "45", 34: "43",
            35: "47", 36: "48", 37: "37", 38: "32", 39: "13", 40: "4", 41: "52", 42: "54",
        }

        self.planning_area_demand = {
            "13": 88.38278669, "17": 12.04196276, "18": 36.17893041,
            "19": 73.00554772, "20": 280.4811969, "21": 76.97281901,
            "22": 54.94081613, "23": 23.71919409, "24": 82.96259741,
            "25": 688.6553387, "26": 197.2051341, "27": 110.8820988,
            "28": 127.2668358, "29": 102.5243876, "30": 122.2662221,
            "31": 100.3836397, "32": 113.4536098, "33": 438.5963687,
            "34": 0.889557235, "35": 290.9455893, "36": 5.963649042,
            "37": 85.62676906, "38": 78.23276669, "39": 54.33080358,
            "4": 27.3007367, "40": 118.4485291, "42": 125.4732716,
            "43": 12.15392398, "44": 162.9562344, "45": 70.62387543,
            "46": 67.82961904, "47": 67.52823509, "48": 167.9488733,
            "49": 11.20478423, "52": 67.60249808, "53": 19.61909364,
            "54": 131.9363219, "55": 24.8988913, "56": 59.55911042,
            "57": 78.63002336, "6": 1117.921164, "60": 1336.999063
        }

    def initialize_city(self):
        self.city_to_population = {
            row["Geographic name"]: {
                "population": row["Population, 2016"],
                "area": row["Land area in square kilometres, 2021"]
            }
            for _, row in self.city_population_df.iterrows()
        }

        self.city_to_coordinates = {
            row["name"]: (row["x"], row["y"])
            for _, row in self.cities_df.iterrows()
        }

    def initialize_coordinates(self):
        self.substations_to_coordinates = {row["substation"]: (row["x"], row["y"]) for _, row in
                                           self.points_df.iterrows()}
        self.coordinates_to_substations = {(row["x"], row["y"]): row["substation"] for _, row in
                                           self.points_df.iterrows()}

    def initialize_line_station_relationships(self):
        for _, row in self.lines_df.iterrows():
            start_candidates = [station for station, coords in self.substations_to_coordinates.items()
                                if coords == (row["Start_X"], row["Start_Y"])]
            end_candidates = [station for station, coords in self.substations_to_coordinates.items()
                              if coords == (row["End_X"], row["End_Y"])]
            if not start_candidates:
                # print(f"Warning: No start station found for coordinates ({row['Start_X']}, {row['Start_Y']})")
                continue
            if not end_candidates:
                # print(f"Warning: No end station found for coordinates ({row['End_X']}, {row['End_Y']})")
                continue

            start_station, end_station = start_candidates[0], end_candidates[0]
            self.lines_to_station_pairs.setdefault(row["line"], []).append((start_station, end_station))
            self.stations_to_lines.setdefault(start_station, []).append(row["line"])
            self.stations_to_lines.setdefault(end_station, []).append(row["line"])
            self.undirect_station_pairs_to_line.setdefault((start_station, end_station), []).append(row["line"])
            self.undirect_station_pairs_to_line.setdefault((end_station, start_station), []).append(row["line"])

        for start, end in self.undirect_station_pairs_to_line.keys():
            if (start, end) not in self.direct_station_pairs_to_line and (
            end, start) not in self.direct_station_pairs_to_line:
                self.direct_station_pairs_to_line[(start, end)] = self.undirect_station_pairs_to_line[(start, end)]

    def initialize_generator_mappings(self):
        for _, row in self.generator_substation_df.iterrows():
            if pd.notnull(row["Substation"]):
                generator_name = row["Generator Name"]
                substation = row["Substation"]

                self.generators_to_substations[generator_name] = substation
                self.generators_to_capacities[generator_name] = row["Maximum Capability"]

                self.substations_to_generators.setdefault(substation, []).append(generator_name)

    def initialize_network_voltage(self):
        self.substations_to_voltage = {row["substation"]: voltage_mapping.get(str(row["voltage"]), None) for _, row in
                                       self.points_df.iterrows()}
        self.lines_to_voltage = {row["Line"]: voltage_mapping.get(str(row["Voltage"]), None) for _, row in
                                 self.line_voltage_df.iterrows()}

    def initialize_border(self):
        self.planning_area_border_edges = [
            ((row["Start_X"], row["Start_Y"]), (row["End_X"], row["End_Y"]))
            for _, row in self.planning_area_border_df.iterrows()
        ]

    def get_city_population_ratio(self):
        total_population = 4262635
        total_city_population = sum([value["population"] for key, value in self.city_to_population.items()])
        print(total_city_population)
        return total_city_population / total_population
