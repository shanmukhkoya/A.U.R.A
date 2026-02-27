"""
CLI script to run benchmarking evaluations.
Usage: python -m evals.run_evals
"""
import sys
import os
import json
import time

# Add root project dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import AutonomousAgent
from agent.config import Config
from agent.providers import get_provider
from evals.evaluator import Evaluator

def main():
    print("🚀 Starting A.U.R.A Benchmarking & Evals Framework\n")
    
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "datasets", "basic_eval.json")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Initialize Agent (The subject being tested)
    config = Config()
    agent = AutonomousAgent(config)
    
    # Initialize Evaluator (The LLM Judge)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # We try to use a powerful model like GPT-4o for judging
        if os.getenv("OPENAI_API_KEY"):
            judge_llm = get_provider("openai", model="gpt-4o-mini")
            print("⚖️  Using GPT-4o-mini as the Evaluator Judge.")
        else:
            judge_llm = get_provider(config.provider_name, **config.provider_config)
            print(f"⚖️  Using {config.provider_name} as the Evaluator Judge (Warning: For robust evals, use GPT-4o or Claude-3.5).")
    except Exception as e:
        print(f"Failed to load judge: {e}")
        return

    evaluator = Evaluator(judge_llm)
    
    results = []

    for item in dataset:
        print(f"\n──────────────────────────────────────────────────")
        print(f"🧪 Testing: {item['id']}")
        print(f"❓ Question: {item['question']}")
        
        # Run agent
        print("\n⏳ Agent is researching... (this may take a few minutes)")
        start_time = time.time()
        
        # Disable logging to keep the console clean for the eval
        agent.set_log_callback(None)
        
        try:
            report = agent.run(item["question"])
            duration = time.time() - start_time
            print(f"✅ Generated report in {duration:.1f} seconds")
            
            # Evaluate report
            print("⚖️  Evaluating output...")
            eval_result = evaluator.benchmark_report(item["question"], item["expected_facts"], report)
            
            eval_result["id"] = item["id"]
            eval_result["time_seconds"] = duration
            results.append(eval_result)
            
            print(f"   Relevance: {eval_result['relevance']}/10")
            print(f"   Accuracy: {eval_result['accuracy']}/10")
            print(f"   Formatting: {eval_result['formatting']}")
            print(f"   Feedback: {eval_result['feedback']}")
        except Exception as e:
            print(f"❌ Eval failed for {item['id']}: {e}")

    # Print summary
    if results:
        print("\n\n📊 Benchmark Summary:")
        print("=====================")
        avg_relevance = sum(r["relevance"] for r in results) / len(results)
        avg_accuracy = sum(r["accuracy"] for r in results) / len(results)
        pass_formatting = sum(1 for r in results if r["formatting"] == "PASS")
        
        print(f"Average Relevance: {avg_relevance:.1f}/10")
        print(f"Average Accuracy:  {avg_accuracy:.1f}/10")
        print(f"Formatting Pass Rate: {pass_formatting}/{len(results)}")
        
    print("\n✅ Evaluations complete.")

if __name__ == "__main__":
    main()
