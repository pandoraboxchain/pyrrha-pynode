# Ethereum Events

Worker node should listen events from the following smart contracts:
* Pandora contract
* Worker node contract
* Cognitive job contract

What should be taken into account:
* New cognitive jobs may be created only under Idle state.
* Worker node contract can change its state in any moment and this
state changes must be handled with the highest priority.
* Cognitive job may change its state asynchroneously. 
This state changes must be handled by calling appropriate worker node
contract methods within some given timeframe.

