%builtins output range_check
from starkware.cairo.common.dict import dict_new, dict_read, dict_write
from starkware.cairo.common.dict_access import DictAccess
from starkware.cairo.common.math import assert_nn_le
from starkware.cairo.common.registers import get_fp_and_pc

const MAX_BALANCE = 2 ** 128 - 1;

struct Account {
    initial_balance: felt,
    balance: felt,
}

struct Transaction {
    from_valut_id: felt,
    to_valut_id: felt,
    amount: felt,
}

struct State {
    account_dict_start: DictAccess*,
    account_dict_end: DictAccess*,
}

struct OutputEntry {
    valut_id: felt,
    amount_before: felt,
    amount_after: felt,
}

func transaction_loop{range_check_ptr}(
    state: State, transactions: Transaction**, transactions_len
) -> (state: State) {
    if (transactions_len == 0) {
        return (state=state);
    }
    alloc_locals;

    let first_transaction: Transaction* = [transactions];

    let account_dict_end = state.account_dict_end;
    
    let from_account_id = first_transaction.from_valut_id;
    let to_account_id = first_transaction.to_valut_id;

    let (old_from_account: Account*) = dict_read{dict_ptr=account_dict_end}(key=from_account_id);
    let (old_to_account: Account*) = dict_read{dict_ptr=account_dict_end}(key=to_account_id);
    tempvar new_from_valut_balance = (old_from_account.balance - first_transaction.amount);
    tempvar new_to_valut_balance = (old_to_account.balance + first_transaction.amount);
    assert_nn_le(new_from_valut_balance, MAX_BALANCE);
    assert_nn_le(new_to_valut_balance, MAX_BALANCE);
    
    local new_from_account: Account;
    local new_to_account: Account;
    assert new_from_account.initial_balance = old_from_account.initial_balance;
    assert new_from_account.balance = new_from_valut_balance;
    assert new_to_account.initial_balance = old_to_account.initial_balance;
    assert new_to_account.balance = new_to_valut_balance;
    let (__fp__, _) = get_fp_and_pc();
    dict_write{dict_ptr=account_dict_end}(key=from_account_id, new_value=cast(&new_from_account, felt));
    dict_write{dict_ptr=account_dict_end}(key=to_account_id, new_value=cast(&new_to_account, felt));

    local new_state: State;
    new_state.account_dict_start = state.account_dict_start;
    new_state.account_dict_end = account_dict_end;

    return transaction_loop(
        state=new_state, transactions=transactions + 1, transactions_len=transactions_len - 1
    );
}

func get_accounts() -> (account_ids: felt*, account_ids_len: felt) {
    alloc_locals;
    local account_ids: felt*;
    local account_ids_len: felt;
    %{
        program_input_accounts = program_input["accounts"]

        account_ids = [
            int(account_id)
            for account_id in program_input_accounts.keys()
        ]
        ids.account_ids = segments.gen_arg(account_ids)
        ids.account_ids_len = len(account_ids)
    %}
    return (account_ids=account_ids, account_ids_len=account_ids_len);
}

func get_transactions() -> (transactions: Transaction**, transactions_len: felt) {
    alloc_locals;
    local transactions: Transaction**;
    local transactions_len: felt;
    %{
        program_input_transactions = program_input["transactions"]

        transactions = [
            (
                int(transaction["from_account_id"]),
                int(transaction["to_account_id"]),
                int(transaction["amount"]),
            )
            for transaction in program_input_transactions
        ]
        ids.transactions = segments.gen_arg(transactions)
        ids.transactions_len = len(transactions)
    %}
    return (transactions=transactions, transactions_len=transactions_len);
}

func get_accounts_dict() -> (account_dict: DictAccess*) {
    alloc_locals;
    %{
        program_input_accounts = program_input["accounts"]

        initial_dict = {
            int(account_id): segments.gen_arg(
                (
                    int(info["balance"]),
                    int(info["balance"]),
                )
            )
            for account_id, info in program_input_accounts.items()
        }
    %}

    let (account_dict) = dict_new();
    return (account_dict=account_dict);
}

func write_output{output_ptr: felt*}(state: State, account_ids: felt*, account_ids_len: felt) -> (output_ptr: felt*, state: State) {
    if (account_ids_len == 0) {
        return (output_ptr=output_ptr, state=state);
    }
    alloc_locals;
    local new_state: State;
    new_state.account_dict_start = state.account_dict_start;
    
    let account_id = account_ids[0];
    let account_dict_end = state.account_dict_end;
    let (account: Account*) = dict_read{dict_ptr=account_dict_end}(key=account_id);
    new_state.account_dict_end = account_dict_end;

    assert output_ptr[0] = account_id;
    assert output_ptr[1] = account.initial_balance;
    assert output_ptr[2] = account.balance;
    let output_ptr = output_ptr + 3;
    
    return write_output(new_state, account_ids + 1, account_ids_len - 1);
}

func verify_account_dict(account_ids: felt*, account_ids_len: felt, account_dict: DictAccess*) -> (account_dict: DictAccess*) {
    if (account_ids_len == 0) {
        return (account_dict=account_dict);
    }
    let account_id = account_ids[0];
    let (account: Account*) = dict_read{dict_ptr=account_dict}(key=account_id);
    assert account.initial_balance = account.balance;
    return verify_account_dict(account_ids + 1, account_ids_len - 1, account_dict);
}

func main{output_ptr: felt*, range_check_ptr}() {
    alloc_locals;

    let (account_ids: felt*, account_ids_len: felt) = get_accounts();
    let (account_dict: DictAccess*) = get_accounts_dict();
    let (account_dict: DictAccess*) = verify_account_dict(account_ids, account_ids_len, account_dict);

    local state: State;
    assert state.account_dict_start = account_dict;
    assert state.account_dict_end = account_dict;

    let (transactions: Transaction**, transactions_len: felt) = get_transactions();

    let (state: State) = transaction_loop(state, transactions, transactions_len);

    let (output_ptr: felt*, state: State) = write_output(state, account_ids, account_ids_len);

    return ();
}
