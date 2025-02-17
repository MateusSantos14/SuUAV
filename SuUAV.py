"""Módulo principal do projeto SuUAV.

Este módulo contém a lógica principal a chamada dos outros modulos.
"""
import argparse
from funcs.parser import parse_config_and_run
from interface.InteractivePlot import run

if __name__ == "__main__":
    '''
    Teste
    '''
    parser = argparse.ArgumentParser(description="SuUAV Application")
    parser.add_argument('--run', action='store_true', help="Start the application with the run configuration")
    parser.add_argument('--setup', action='store_true', help="Start the setup with the setup configuration")
    parser.add_argument('-i', '--input', type=str, help="Path to the input file for setup or run")

    args = parser.parse_args()

    if args.setup:
        if args.input:
            run(args.input)
        else:
            print("Error: --input argument is required for --setup")
    elif args.run:
        if args.input:
            parse_config_and_run(args.input)
        else:
            print("Error: --input argument is required for --run")
    else:
        print("Error: No valid command provided. Use --setup or --run")