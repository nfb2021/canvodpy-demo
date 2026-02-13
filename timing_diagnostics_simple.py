#!/usr/bin/env python3
"""Timing Diagnostics - Single Day Processing

Simplified script for processing one day of GNSS data with timing analysis.
This is a standalone version that can be run directly (not as a notebook).

Usage:
    python timing_diagnostics_simple.py

Author: Nicolas François Bader
Date: 2025-01-21
"""

import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from gnssvodpy.globals import KEEP_RNX_VARS
from gnssvodpy.icechunk_manager.manager import GnssResearchSite
from gnssvodpy.processor.pipeline_orchestrator import (
    PipelineOrchestrator,
)


def format_time(seconds: float) -> str:
    """Format seconds into a human-readable duration string.

    Parameters
    ----------
    seconds : float
        Duration in seconds.

    Returns
    -------
    str
        Human-readable duration.

    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    hours = seconds / 3600
    return f"{hours:.2f}h"


def print_header(title: str) -> None:
    """Print a formatted header line.

    Parameters
    ----------
    title : str
        Header text to display.

    """
    print(f"\n{'=' * 80}")
    print(f"{title.center(80)}")
    print(f"{'=' * 80}\n")


def print_section(title: str) -> None:
    """Print a formatted section header line.

    Parameters
    ----------
    title : str
        Section title to display.

    """
    print(f"\n{'─' * 80}")
    print(f"{title}")
    print(f"{'─' * 80}")


def run_diagnostics(
    target_date: str = "2025001",
    site_name: str = "Rosalia",
) -> None:
    """Run timing diagnostics for one day of GNSS data.

    Parameters
    ----------
    target_date : str
        Date in YYYYDOY format (e.g., "2025001" for Jan 1, 2025).
    site_name : str
        Name of the research site.

    Returns
    -------
    None
        This function prints diagnostics to stdout and writes a CSV report.

    """
    print_header("GNSS VOD PROCESSING - TIMING DIAGNOSTICS")

    print("Configuration:")
    print(f"  Site: {site_name}")
    print(f"  Target Date: {target_date}")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"  Start Time: {start_time}")
    print()

    # ========================================================================
    # Step 1: Initialize Site
    # ========================================================================

    print_section("STEP 1: Initialize Research Site")

    init_start = time.time()
    try:
        site = GnssResearchSite(site_name=site_name)
        init_time = time.time() - init_start

        active_receivers = sorted(site.active_receivers.keys())
        print(f"✓ Site initialized in {format_time(init_time)}")
        print(f"  Active receivers: {len(active_receivers)}")
        for receiver in active_receivers:
            print(f"    - {receiver}")
    except Exception as e:
        print(f"✗ Failed to initialize site: {e}")
        return

    # ========================================================================
    # Step 2: Create Orchestrator
    # ========================================================================

    print_section("STEP 2: Create Pipeline Orchestrator")

    orch_start = time.time()
    try:
        orchestrator = PipelineOrchestrator(site=site, dry_run=False)
        orch_time = time.time() - orch_start
        print(f"✓ Orchestrator created in {format_time(orch_time)}")
    except Exception as e:
        print(f"✗ Failed to create orchestrator: {e}")
        return

    # ========================================================================
    # Step 3: Process Target Date
    # ========================================================================

    print_section(f"STEP 3: Process {target_date}")

    receiver_times = {}
    datasets = {}
    total_start = time.time()

    try:
        # Process one day
        for date_key, ds_dict, time_dict in orchestrator.process_by_date(
            keep_vars=KEEP_RNX_VARS,
            start_from=target_date,
            end_at=target_date,
        ):
            datasets = ds_dict
            receiver_times = time_dict
            break  # Only process one day

        total_time = time.time() - total_start

        if not datasets:
            print(f"⚠ No data processed for {target_date}")
            print("  Possible reasons:")
            print("    - No RINEX files available for this date")
            print("    - Files already processed")
            return

        print(f"✓ Processing complete in {format_time(total_time)}")
        print()

        # ====================================================================
        # Step 4: Display Results
        # ====================================================================

        print_section("STEP 4: Results Summary")

        # Create summary table
        header = (
            f"\n{'Receiver':<15} {'Time':<10} {'Epochs':<8} {'SVs':<6} "
            f"{'Observations':<12}"
        )
        print(header)
        print(f"{'-' * 60}")

        total_epochs = 0
        total_svs = 0
        total_obs = 0

        for receiver_name, ds in datasets.items():
            epochs = ds.sizes.get("epoch", 0)
            svs = ds.sizes.get("sv", 0)
            obs = epochs * svs

            total_epochs += epochs
            total_svs += svs
            total_obs += obs

            row = (
                f"{receiver_name:<15} {receiver_times[receiver_name]:>8.2f}s "
                f"{epochs:>7,} {svs:>5} {obs:>11,}"
            )
            print(row)

        print(f"{'-' * 60}")
        total_row = (
            f"{'TOTAL':<15} {total_time:>8.2f}s {total_epochs:>7,} "
            f"{total_svs:>5} {total_obs:>11,}"
        )
        print(total_row)

        # ====================================================================
        # Step 5: Performance Metrics
        # ====================================================================

        print_section("STEP 5: Performance Metrics")

        avg_time = sum(receiver_times.values()) / len(receiver_times)
        fastest = min(receiver_times.values())
        slowest = max(receiver_times.values())
        fastest_receiver = min(receiver_times, key=receiver_times.get)
        slowest_receiver = max(receiver_times, key=receiver_times.get)

        throughput = total_obs / total_time if total_time > 0 else 0

        print("\nTiming Statistics:")
        print(f"  Total time:     {format_time(total_time)}")
        print(f"  Average/recv:   {format_time(avg_time)}")
        print(f"  Fastest:        {format_time(fastest)} ({fastest_receiver})")
        print(f"  Slowest:        {format_time(slowest)} ({slowest_receiver})")
        print()
        print("Throughput:")
        print(f"  Observations:   {total_obs:,}")
        print(f"  Rate:           {throughput:,.0f} obs/s")
        per_receiver = throughput / len(datasets)
        print(f"  Per receiver:   {per_receiver:,.0f} obs/s")

        # ====================================================================
        # Step 6: Save Report
        # ====================================================================

        print_section("STEP 6: Save Timing Report")

        # Create report DataFrame
        report_data = {
            "date": [target_date],
            "start_time": [datetime.now().isoformat()],
            "total_seconds": [total_time],
            "total_epochs": [total_epochs],
            "total_observations": [total_obs],
            "throughput_obs_per_sec": [throughput],
        }

        # Add receiver times
        for receiver_name, time_val in receiver_times.items():
            report_data[f"{receiver_name}_seconds"] = [time_val]

        report_df = pd.DataFrame(report_data)

        # Save to CSV
        output_dir = Path(__file__).parent
        output_file = output_dir / f"timing_report_{target_date}.csv"

        try:
            report_df.to_csv(output_file, index=False)
            print(f"✓ Report saved to: {output_file.absolute()}")
        except Exception as e:
            print(f"✗ Failed to save report: {e}")

        # Display report
        print("\nReport Preview:")
        print(report_df.to_string(index=False))

    except Exception as e:
        print(f"✗ Processing failed: {e}")
        import traceback

        traceback.print_exc()
        return

    # ========================================================================
    # Final Summary
    # ========================================================================

    print_header("DIAGNOSTICS COMPLETE")

    print(f"Successfully processed {target_date}")
    print(f"Total time: {format_time(total_time)}")
    print(f"Receivers processed: {len(datasets)}")
    print(f"Total observations: {total_obs:,}")
    print()
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"End time: {end_time}")
    print()


if __name__ == "__main__":
    # Process January 1, 2025 (DOY 001)
    run_diagnostics(target_date="2025001", site_name="Rosalia")

    # To process a different date, modify the target_date parameter:
    # run_diagnostics(target_date="2025002")  # January 2, 2025
    # run_diagnostics(target_date="2024365")  # December 31, 2024
