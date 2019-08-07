from tokenizer import word_tokenize_return_string_and_length

class Record(object):
    def __init__(self, type, entity, value, tokenized=False):
        self.type = type
        self.entity = entity
        self.value = value
        self.delexicalized_value = value
        self.delexicalized_entity = entity
        self.tokenized = False
        self.values_not_to_delexicalize = ["dont_care", "dontcare", "none", "yes", "no", "false", "true"]

    @property
    def length(self):
        return len(self.type + self.entity + self.value)

    @property
    def num_tokens(self):
        num_tokens_type = len(self.type.split())
        num_tokens_entity = len(self.entity.split())
        num_tokens_value = len(self.value.split())

        return num_tokens_type + num_tokens_entity + num_tokens_value

    def tokenize(self):
        self.tokenized = True
        self.type, num_tokens_type = word_tokenize_return_string_and_length(self.type)
        self.entity, num_tokens_entity = word_tokenize_return_string_and_length(self.entity)
        self.value, num_tokens_value = word_tokenize_return_string_and_length(self.value)

    def lowercase(self):
        self.type = self.type.lower()
        self.entity = self.entity.lower()
        self.value = self.value.lower()

    def maybe_set_delexicalized_entity_or_value(self, string_to_delexicalize, delex_string):
        if string_to_delexicalize == self.value:
            self.set_delexicalized_value(delex_string)
        elif string_to_delexicalize == self.entity:
            self.set_delexicalized_entity(delex_string)

    def set_delexicalized_value(self, delexicalized_value=""):
        if self.value not in self.values_not_to_delexicalize: # do not delexicalize dont_care, yes/no etc.
            if delexicalized_value:
                self.delexicalized_value = delexicalized_value
            else:
                self.delexicalized_value = self.entity.upper() + "-X"

    def set_delexicalized_entity(self, delexicalized_entity=""):
        if delexicalized_entity:
            self.delexicalized_entity = delexicalized_entity
        else:
            self.delexicalized_entity = self.type.upper() + "-X"

    def delexicalize(self, delexicalized_string):
        if delexicalized_string == self.value:
            self.value = self.delexicalized_value
        if delexicalized_string == self.entity:
            self.entity = self.delexicalized_entity

    def lexicalize(self, relex_dict):
        for delex_string in relex_dict:
            if delex_string == self.entity:
                self.entity = relex_dict[delex_string][0]
            if delex_string == self.value:
                self.value = relex_dict[delex_string][0]

    def as_string(self, flat):
        """
        only write type if it is not ""
        :param tokenized:
        :return:
        """
        if self.type == "":
            if flat:
                string_format = "%s %s"
            elif self.tokenized:
                string_format = "%s [ %s ]"
            else:
                string_format = "%s[%s]"

            string = (string_format % (self.entity, self.value))

        # we have a type
        else:
            if flat:
                    string_format = "%s %s %s"
            elif self.tokenized:
                string_format = "%s ( %s [ %s ] )"
            else:
                string_format = "%s(%s[%s])"

            string = (string_format %(self.type, self.entity, self.value))

        return string.encode("utf-8")