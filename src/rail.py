class Rail:
    def __init__(self):
        self.train = None

    def launch_train(self, t):
        """
        :param t: Train
        :return:
        """
        self.train = t

    def get_train(self):
        return self.train

    def is_rail_full(self):
        return self.train is not None

    def clear_rail(self):
        self.train = None
