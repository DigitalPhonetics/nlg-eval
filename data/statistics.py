class Statistics():
    def __init__(self, name):
        self.name = name
        self.min = 100000000000
        self.max = 0
        self.total = 0
        self.instances = 0

    def update(self, value):
        """
        updates min, max, total with the given value
        :param value:
        :param min:
        :param max:
        :param total:
        :return:
        """
        if value < self.min:
            self.min = value
        if value > self.max:
            self.max = value
        self.total += value
        self.instances += 1

    def update_from_statistics_object(self, statistics):
        if statistics.min < self.min:
            self.min = statistics.min
        if statistics.max > self.max:
            self.max = statistics.max
        self.total += statistics.total
        self.instances += statistics.instances


    def get_average(self):
        if self.instances == 0:
            return 0.0
        else:
            return self.total / float(self.instances)


    def as_string(self):
        string = "%s\t min: %d, max: %d, average: %.2f, instances: %d" %(self.name, self.min, self.max, self.get_average(), self.instances)
        return string