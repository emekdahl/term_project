from itertools import product
import pandas as pd
import random
import simpy

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def customer_request(env, name, ai_deflection_rates, human_support_L1, human_support_L2, stats):
    arrival_time = env.now
    request_type = random.choice(['simple', 'complex'])
    ai_deflection_rate = ai_deflection_rates[request_type]
    if random.uniform(0, 1) < ai_deflection_rate:
        ai_resolution_time = random.expovariate(1/1)
        yield env.timeout(ai_resolution_time)
        stats['customers_resolved_by_AI'] += 1
    else:
        queue_length = len(human_support_L1.queue)
        balking_threshold = random.randint(1, 3)
        if queue_length >= balking_threshold:
            stats['balked_customers'] += 1
            return
        else:
            reneging_threshold = random.uniform(2, 5)
            patience = env.timeout(reneging_threshold)
            req = human_support_L1.request()
            waiting_start = env.now
            results = yield req | patience
            waiting_time = env.now - waiting_start
            if req in results:
                stats['wait_times_L1'].append(waiting_time)
                stats['customers_served_L1'] += 1
                service_start = env.now
                L1_resolution_time = random.expovariate(1/7)
                yield env.timeout(L1_resolution_time)
                service_time = env.now - service_start
                stats['service_times_L1'].append(service_time)
                yield human_support_L1.release(req)
                if request_type == 'complex' and random.uniform(0, 1) < 0.8:
                    yield env.process(level2_support(env, name, human_support_L2, stats))
                else:
                    pass
            else:
                stats['reneged_customers_L1'] += 1
                req.cancel()

def level2_support(env, name, human_support_L2, stats):
    with human_support_L2.request() as request:
        waiting_start = env.now
        patience_time = random.uniform(3, 7)
        patience = env.timeout(patience_time)
        results = yield request | patience
        waiting_time = env.now - waiting_start
        if request in results:
            stats['wait_times_L2'].append(waiting_time)
            stats['customers_served_L2'] += 1
            L2_resolution_time = random.expovariate(1/13)
            yield env.timeout(L2_resolution_time)
            service_time = env.now - (waiting_start + waiting_time)
            stats['service_times_L2'].append(service_time)
        else:
            stats['reneged_customers_L2'] += 1

def customer_arrivals(env, arrival_rate, ai_deflection_rates, human_support_L1, human_support_L2, stats):
    customer_id = 0
    while True:
        interarrival_time = random.expovariate(arrival_rate)
        yield env.timeout(interarrival_time)
        customer_id += 1
        name = f'Customer {customer_id}'
        env.process(customer_request(env, name, ai_deflection_rates, human_support_L1, human_support_L2, stats))

def run_simulation(num_L1_agents, num_L2_agents, ai_deflection_rates, sim_time, arrival_rate):
    stats = {
        'wait_times_L1': [],
        'wait_times_L2': [],
        'service_times_L1': [],
        'service_times_L2': [],
        'balked_customers': 0,
        'reneged_customers_L1': 0,
        'reneged_customers_L2': 0,
        'customers_served_L1': 0,
        'customers_served_L2': 0,
        'customers_resolved_by_AI': 0,
    }

    env = simpy.Environment()
    human_support_L1 = simpy.Resource(env, capacity=num_L1_agents)
    human_support_L2 = simpy.Resource(env, capacity=num_L2_agents)

    env.process(customer_arrivals(env, arrival_rate, ai_deflection_rates, human_support_L1, human_support_L2, stats))
    env.run(until=sim_time)
    return stats

if __name__ == "__main__":
    AI_DEFLECTION_RATES = {
        'simple': float(input("Enter AI resolution rate for simple cases (0-1): ")),
        'complex': float(input("Enter AI resolution rate for complex cases (0-1): "))
    }
    SIM_TIME = 480
    ARRIVAL_RATE = 1/0.05

    MAX_WAIT_L1 = 2
    MAX_WAIT_L2 = 5

    results = []
    max_agents = 10
    num_runs = 10

    combinations = list(product(range(2, max_agents+1), repeat=2))

    for num_L1_agents, num_L2_agents in combinations:
        avg_wait_L1_list = []
        avg_wait_L2_list = []
        for _ in range(num_runs):
            stats = run_simulation(num_L1_agents, num_L2_agents, AI_DEFLECTION_RATES, SIM_TIME, ARRIVAL_RATE)
            avg_wait_L1 = sum(stats['wait_times_L1']) / len(stats['wait_times_L1']) if stats['wait_times_L1'] else float('inf')
            avg_wait_L2 = sum(stats['wait_times_L2']) / len(stats['wait_times_L2']) if stats['wait_times_L2'] else float('inf')
            avg_wait_L1_list.append(avg_wait_L1)
            avg_wait_L2_list.append(avg_wait_L2)
        avg_wait_L1 = sum(avg_wait_L1_list) / len(avg_wait_L1_list)
        avg_wait_L2 = sum(avg_wait_L2_list) / len(avg_wait_L2_list)

        if avg_wait_L1 <= MAX_WAIT_L1 and avg_wait_L2 <= MAX_WAIT_L2:
            results.append({
                'L1 Agents': num_L1_agents,
                'L2 Agents': num_L2_agents,
                'Avg Wait L1 (min)': round(avg_wait_L1, 2),
                'Avg Wait L2 (min)': round(avg_wait_L2, 2)
            })

    if results:
        df_results = pd.DataFrame(results)
        df_results['Total Agents'] = df_results['L1 Agents'] + df_results['L2 Agents']
        df_results.sort_values(by=['Total Agents', 'L1 Agents', 'L2 Agents'], inplace=True)
        print("\nPossible Staffing Combinations to Meet Performance Criteria:")
        print(df_results[['L1 Agents', 'L2 Agents', 'Avg Wait L1 (min)', 'Avg Wait L2 (min)', 'Total Agents']].to_string(index=False))
    else:
        print("\nNo combination of agents found within the specified range that meets the performance criteria.")
