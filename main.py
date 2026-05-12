from concurrent.futures import ProcessPoolExecutor
import argparse

from agent import Agent
from ports import generate_ports


def run_agent(agent_id, port):

    agent = Agent(agent_id, port)

    return agent.run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agents",
        type=int,
        default=1,
        help="Number of agents"
    )

    args = parser.parse_args()

    NUM_AGENTS = args.agents

    ports = generate_ports(
        # seed=1337,
        n=NUM_AGENTS,
    )

    with ProcessPoolExecutor(max_workers=NUM_AGENTS) as pool:

        futures = []

        for i, port in enumerate(ports):

            futures.append(
                pool.submit(run_agent, i, port)
            )

        results = [f.result() for f in futures]

    print(results)