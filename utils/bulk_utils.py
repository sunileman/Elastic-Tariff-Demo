from elasticsearch import helpers


def bulk_index_to_es(es, records, index_name):

    successes = 0
    failed_count = 0

    # Using parallel_bulk for improved throughput
    for success, info in helpers.parallel_bulk(es, records, index=index_name, thread_count=4, chunk_size=500):
        if not success:
            print("A document failed:", info)
            failed_count += 1
        else:
            successes += 1

    return successes, failed_count
