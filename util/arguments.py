class DatsetArguments:
    def __init__(self, dataset_path, dataset_type, output_path, only_source=False, multi_reference=False,
                 lowercase=False,
                 tokenize=False,
                 delexicalize=False, delexicalize_after_grouping=False,
                 group_inputs=False,
                 collect_multi_references=False,
                 entities_to_delexicalize=None,
                 log_level="info",
                 randomize_record_order=False,
                 record_delimiter=" , ", flatten_records=False,
                 separate_inputs_for_number_of_records=False,
                 tokenize_src=None, tokenize_tgt=None):

        self.dataset_path = dataset_path
        self.dataset_type = dataset_type
        self.output_path = output_path + "_src.txt"
        self.only_source = only_source

        self.multi_reference = multi_reference
        self.lowercase = lowercase

        self.tokenize = tokenize
        if not tokenize_src:
            tokenize_src = tokenize
        if not tokenize_tgt:
            tokenize_tgt = tokenize
        self.tokenize_src = tokenize_src
        self.tokenize_tgt = tokenize_tgt

        self.delexicalize = delexicalize
        self.delexicalize_after_grouping = delexicalize_after_grouping
        self.group_inputs = group_inputs
        self.collect_multi_references = collect_multi_references

        self.output_path_references = output_path + "_tgt.txt"  # output_path_references
        self.relexicalization_file = output_path + "_relex.txt"

        if entities_to_delexicalize is None:
            entities_to_delexicalize = []
        self.entities_to_delexicalize = entities_to_delexicalize
        self.log_level = log_level

        self.randomize_record_order = randomize_record_order
        self.record_delimiter = record_delimiter
        self.flatten_records = flatten_records
        self.separate_inputs_for_number_of_records = separate_inputs_for_number_of_records
