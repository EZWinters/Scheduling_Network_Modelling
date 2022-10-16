class Activity:
    def __init__(self, label, duration):
        self.label = label
        self.duration = duration
        self.level = None
        self.early_start = None
        self.early_finish = None
        self.late_start = None
        self.late_finish = None
        self.total_float = None
        self.free_float = None
        self.successors = []

    def __str__(self):
        delimiter = "-"
        successor_labels = [successor.label for successor in self.successors]
        return self.label + ',' + 'duration:' + str(self.duration) + ',' + 'early_start:' + str(
            self.early_start) + ',' + 'early_finish:' + str(self.early_finish) + ',' + 'late_start:' + str(
            self.late_start) + ',' + 'late_finish:' + str(self.late_finish) + ',' + 'total_float:' + str(
            self.total_float) + ',' + 'free_float:' + str(self.free_float) + ',' + delimiter.join(
            successor_labels) + ',' + 'level:' + str(self.level)