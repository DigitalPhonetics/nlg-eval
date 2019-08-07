def dataset_options(parser):

    parser.add_argument('dataset_path', action='store', help='Path to dataset file')
    parser.add_argument('dataset_type', choices=['webnlg', 'e2e', "rnnlg", "bagel", "preprocessed", "preprocessed-webnlg"],
                        help='Type of input dataset')
    parser.add_argument('--output_path', help='Path to common format output dataset')
    parser.add_argument('--only_source', action="store_true", help='Only read source')
    parser.add_argument('--multi_reference', action="store_true",
                        help='Read targets in multi-ref mode (for webNLG means only read targets)')
    parser.add_argument('--lowercase', action="store_true", help='Lowercase inputs and targets')
    parser.add_argument('--tokenize', action="store_true", help='Tokenize inputs and targets')
    parser.add_argument('--tokenize_src', action="store_true", help='Only tokenize inputs')
    parser.add_argument('--tokenize_tgt', action="store_true", help='Only tokenize targets')
    parser.add_argument('--delexicalize', action="store_true", help='Delexicalize inputs and targets before grouping')
    parser.add_argument('--delexicalize_after_grouping', action="store_true",
                        help='Delexicalize inputs and targets after grouping, not before')
    parser.add_argument('--group_inputs', action="store_true", help='Group targets for instances which have the same input')
    parser.add_argument('--collect_multi_references', action="store_true",
                        help='Relexicalize all possible references for the delexicalized input, yields lexicalized inputs and multiple targets')
    parser.add_argument('--randomize_record_order', action="store_true", help='Randomize the order of the records in each input')
    parser.add_argument('--output_path_references',
                        help='Separate output file for references if only_targets or group_inputs are set')
    parser.add_argument('--record_delimiter', type=str, default=" , ", help="Delimiter of records in input")
    parser.add_argument('--flatten_records',
                        help='If set, record type, entity and value in input are cocatenated by whitespace'
                             ' instead of nested bracket representation')
    parser.add_argument('--relexicalization_file', help='File to write/load from relexicalization information')
    parser.add_argument('--entities_to_delexicalize', nargs="+", default=[],
                        help='Name of entities that should be delexicalized separated by whitespace.')
    parser.add_argument('--log-level', dest='log_level',
                        default='info',
                        help='Logging level')
    parser.add_argument('--separate_inputs_for_number_of_records', action="store_true",
                        help="Create separate src files for each number of input records")

    return parser

def baseline_options(parser):
    parser.add_argument('test_dataset_path', action='store', help='Path to test dataset file')
    return parser