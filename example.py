import simpy
import random
import csv

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def customer_request(env, name, ai_deflection_rates, human_support_L1, human_support_L2, writer):
    """
    Simulates a customer request being handled by AI or human support, including potential escalation.
    """
    arrival_time = env.now
    writer.writerow([arrival_time, name, 'Arrived'])
    print(f'{arrival_time:.2f} - {name}: Request arrived.')

    request_type = random.choice(['simple', 'complex'])
    writer.writerow([env.now, name, f'Request type: {request_type}'])
    print(f'{env.now:.2f} - {name}: Request type is {request_type}.')

    ai_deflection_rate = ai_deflection_rates[request_type]

    if random.uniform(0, 1) < ai_deflection_rate:
        ai_resolution_time = random.expovariate(1/1)  # Mean resolution time of 1 minute
        yield env.timeout(ai_resolution_time)
        completion_time = env.now
        writer.writerow([completion_time, name, 'Resolved by AI'])
        print(f'{completion_time:.2f} - {name}: Resolved by AI.')
    else:

        writer.writerow([env.now, name, 'Queued for Level 1 Support'])
        print(f'{env.now:.2f} - {name}: Queued for Level 1 support.')

        with human_support_L1.request() as request:
            yield request
            start_time = env.now
            writer.writerow([start_time, name, 'Level 1 Support Started'])
            print(f'{start_time:.2f} - {name}: Level 1 support started.')

            L1_resolution_time = random.expovariate(1/5)  # Mean resolution time of 5 minutes
            yield env.timeout(L1_resolution_time)
            completion_time = env.now

            if request_type == 'complex' and random.uniform(0, 1) < 0.8:
                writer.writerow([completion_time, name, 'Escalated to Level 2'])
                print(f'{completion_time:.2f} - {name}: Escalated to Level 2 support.')

                writer.writerow([env.now, name, 'Queued for Level 2 Support'])
                with human_support_L2.request() as request_L2:
                    yield request_L2
                    start_time_L2 = env.now
                    writer.writerow([start_time_L2, name, 'Level 2 Support Started'])
                    print(f'{start_time_L2:.2f} - {name}: Level 2 support started.')

                    L2_resolution_time = random.expovariate(1/10)  # Mean resolution time of 10 minutes
                    yield env.timeout(L2_resolution_time)
                    completion_time_L2 = env.now
                    writer.writerow([completion_time_L2, name, 'Resolved by Level 2'])
                    print(f'{completion_time_L2:.2f} - {name}: Resolved by Level 2 support.')
            else:
                writer.writerow([completion_time, name, 'Resolved by Level 1'])
                print(f'{completion_time:.2f} - {name}: Resolved by Level 1 support.')

def customer_arrivals(env, arrival_rate, ai_deflection_rates, human_support_L1, human_support_L2, writer):
    """
    Generates customer requests at a given arrival rate.
    """
    customer_id = 0
    while True:
        interarrival_time = random.expovariate(arrival_rate)
        yield env.timeout(interarrival_time)
        customer_id += 1
        name = f'Customer {customer_id}'
        env.process(customer_request(env, name, ai_deflection_rates, human_support_L1, human_support_L2, writer))

def run_simulation(num_L1_agents, num_L2_agents, ai_deflection_rates, sim_time, arrival_rate):
    """
    Runs the customer support simulation.
    """
    with open('customer_support_events.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Customer', 'Event'])
        
        env = simpy.Environment()
        human_support_L1 = simpy.Resource(env, capacity=num_L1_agents)
        human_support_L2 = simpy.Resource(env, capacity=num_L2_agents)
        
        env.process(customer_arrivals(env, arrival_rate, ai_deflection_rates, human_support_L1, human_support_L2, writer))
        
        env.run(until=sim_time)

    print("\nSimulation complete. Event log saved to 'customer_support_events.csv'.")

NUM_L1_AGENTS = 5
NUM_L2_AGENTS = 2
AI_DEFLECTION_RATES = {
    'simple': 0.7,
    'complex': 0.4
}
SIM_TIME = 480
ARRIVAL_RATE = 1/2

run_simulation(NUM_L1_AGENTS, NUM_L2_AGENTS, AI_DEFLECTION_RATES, SIM_TIME, ARRIVAL_RATE)
