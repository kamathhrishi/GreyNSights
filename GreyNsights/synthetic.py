from DataSynthesizer.DataDescriber import DataDescriber
from DataSynthesizer.DataGenerator import DataGenerator
from DataSynthesizer.ModelInspector import ModelInspector
from DataSynthesizer.lib.utils import read_json_file, display_bayesian_network


class SyntheticData:
    def __init__(self, path, epsilon=1.0, categorical=None, candidate_keys=None):

        self.mode = "random_mode"
        self.input_data = path
        self.description_file = "description_1.json"
        self.synthetic_data = "sythetic_data.csv"
        self.epsilon = epsilon
        self.categorical_attributes = categorical
        self.candidate_keys = candidate_keys

    def random(self):
        # An attribute is categorical if its domain size is less than this threshold.
        # Here modify the threshold to adapt to the domain size of "education" (which is 14 in input dataset).
        threshold_value = 20

        # Number of tuples generated in synthetic dataset.
        num_tuples_to_generate = len(
            self.input_data
        )  # Here 32561 is the same as input dataset, but it can be set to another number.

        describer = DataDescriber(category_threshold=threshold_value)
        describer.describe_dataset_in_random_mode(self.input_data)
        describer.save_dataset_description_to_file(self.description_file)

        generator = DataGenerator()
        generator.generate_dataset_in_random_mode(
            num_tuples_to_generate, self.description_file
        )
        # generator.save_synthetic_data(self.synthetic_data)

        return generator.synthetic_dataset

    def fit(self):
        # An attribute is categorical if its domain size is less than this threshold.
        # Here modify the threshold to adapt to the domain size of "education" (which is 14 in input dataset).
        threshold_value = 20
        # specify categorical attributes
        self.categorical_attributes = {"education": True}
        # specify which attributes are candidate keys of input dataset.
        self.candidate_keys = {"ssn": True}
        # A parameter in Differential Privacy. It roughly means that removing a row in the input dataset will not
        # change the probability of getting the same output more than a multiplicative difference of exp(epsilon).
        # Increase epsilon value to reduce the injected noises. Set epsilon=0 to turn off differential privacy.
        # The maximum number of parents in Bayesian network, i.e., the maximum number of incoming edges.
        degree_of_bayesian_network = 2
        # Number of tuples generated in synthetic dataset.
        num_tuples_to_generate = len(
            self.input_data
        )  # Here 32561 is the same as input dataset, but it can be set to another number.
        describer = DataDescriber(category_threshold=threshold_value)
        describer.describe_dataset_in_correlated_attribute_mode(
            dataset_file=self.input_data,
            epsilon=self.epsilon,
            k=degree_of_bayesian_network,
            attribute_to_is_categorical=self.categorical_attributes,
            attribute_to_is_candidate_key=self.candidate_keys,
        )
        describer.save_dataset_description_to_file(self.description_file)

        generator = DataGenerator()
        generator.generate_dataset_in_correlated_attribute_mode(
            num_tuples_to_generate, self.description_file
        )

        return generator.synthetic_dataset
