import math
import random
from server.simulation.simulation import SimulationModule, SimulationContext, TickContext, SimulationModuleData
from server import devices


class FuelNode:
    """Represents a single axial slice/node within a fuel assembly."""
    def __init__(self, node_index, total_nodes):
        self.node_index = node_index
        self.total_nodes = total_nodes

        # Axial distribution: Steam quality naturally increases as you go up the core
        self.steam_quality = (node_index / total_nodes) * 0.4

        self.insertion = 1.0  # Fraction of this node covered by control rod (0.0 to 1.0)
        self.temperature = 293.0  # Kelvin
        self.neutron_population = 24.0
        self.startup_source = 5.2

        self.reactivity_bias = random.uniform(-0.0055, 0.0055)

    def GetKeff(self, effective_insertion=None):
        ins = self.insertion if effective_insertion is None else effective_insertion
        
        # Physics factors
        fast_fission = 1.04 + (0.00875 * self.steam_quality)
        fast_nonleakage = 0.865
        resonance_escape = (0.957 - (0.10 * self.steam_quality)) - (0.00392 * math.sqrt(self.temperature))
        
        lt_unrod = 0.95 - (0.04 * self.steam_quality)
        lt_rod = 0.861 - (0.02 * self.steam_quality)
        thermal_nonleakage = ((1.0 - ins) * lt_unrod) + (ins * lt_rod)
        
        f_unrod = 0.85 - (0.1375 * self.steam_quality)
        f_rod = 0.60 - (0.03 * self.steam_quality)
        thermal_utilization = ((1.0 - ins) * f_unrod) + (ins * f_rod)
        
        reproduction = 2.02

        base_keff = (fast_fission * fast_nonleakage * resonance_escape * 
                     thermal_nonleakage * thermal_utilization * reproduction)
        return base_keff + self.reactivity_bias


class FuelAssembly:
    """Represents a full vertical fuel assembly consisting of multiple axial slices."""
    def __init__(self, rod_name, num_slices=24):
        self.rod_name = rod_name
        self.num_slices = num_slices
        self.notch = 0
        
        # Internal stack of axial nodes
        self.nodes = [FuelNode(z, num_slices) for z in range(num_slices)]

    def SetPosition(self, notch):
        self.notch = max(0, min(48, notch))
        # Continuous rod tip position in terms of node index (0 to num_slices)
        rod_tip_position = (self.notch / 48.0) * self.num_slices

        # BWR control rods insert from the BOTTOM (node 0 up towards num_slices)
        for z, node in enumerate(self.nodes):
            if rod_tip_position <= z:
                # Rod hasn't reached this node yet -> Fully inserted/shielded by rod below
                node.insertion = 1.0
            elif rod_tip_position >= z + 1:
                # Rod withdrawn past this node entirely
                node.insertion = 0.0
            else:
                # Partial insertion for intermediate notch positions
                node.insertion = 1.0 - (rod_tip_position - z)

    def __getitem__(self, idx):
        """Allows direct indexing like assembly[z] to access axial nodes."""
        return self.nodes[idx]

    def __len__(self):
        return len(self.nodes)


class SRMDetector:
    def __init__(self, core_channel_assembly, target_slice):
        self.assembly = core_channel_assembly
        self.target_slice = target_slice
        self.LastNeutronCount = 100.0  

    def GetFlux(self):
        return self.assembly[self.target_slice].neutron_population
    
    def GetPeriod(self, delta_t):
        flux = self.GetFlux()
        if flux <= 0 or self.LastNeutronCount <= 0 or flux == self.LastNeutronCount:
            self.LastNeutronCount = flux
            return float('inf')
            
        period = delta_t / math.log(flux / self.LastNeutronCount)
        self.LastNeutronCount = flux
        return period

class ReactorSimulationData(SimulationModuleData):
    reactor_matrix = []
    num_slices = 24
    SRMA: SRMDetector


class Reactor(SimulationModule):
    State = ReactorSimulationData()
    _data = SimulationModuleData()
    def __init__(self):
        super().__init__()

        self._data.State = self.State

        template = [
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],#47
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#43
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#39
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#35
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#31
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#27
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#23
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],#19
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],#15
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],#11
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],#07
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0] #03
        ]
        
        for r in range(len(template)):
            row_list = []
            for c in range(len(template[0])):
                if template[r][c] == 1:
                    rodx = (c*4)+2
                    if rodx <= 9:
                        rodx = f"0{rodx}"
                    rody = (abs(r-(len(template[0])-1))*4)+3
                    if rody <= 9:
                        rody = f"0{rody}"

                    print(rodx,rody)
                    assembly = FuelAssembly(rod_name=f"{rodx}-{rody}", num_slices=self.State.num_slices)
                    row_list.append(assembly)
                else:
                    row_list.append(0)
            self.State.reactor_matrix.append(row_list)
            
        self.State.SRMA = SRMDetector(self.State.reactor_matrix[3][3], target_slice=6)

    def OnRegister(self,world:SimulationContext) -> None:

        world.SimulationStateRegistry.SetState("reactor",self._data)

    def OnTick(self, world: SimulationContext, ctx: TickContext):
        delta_t = ctx.Delta

        rows = len(self.State.reactor_matrix)
        cols = len(self.State.reactor_matrix[0])
        delta_n_matrix = [[[0.0 for _ in range(self.State.num_slices)] for _ in range(cols)] for _ in range(rows)]
        
        radial_diffusion_rate = 0.8 * delta_t 
        axial_diffusion_rate = 0.4 * delta_t 

        for r in range(rows):
            for c in range(cols):
                assembly = self.State.reactor_matrix[r][c]
                if assembly == 0:
                    continue
                
                for z in range(self.State.num_slices):
                    node = assembly[z]
                    n_current = node.neutron_population
                    
                    neighbors_coords = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
                    total_insertion = node.insertion
                    valid_count = 1
                    
                    for nr, nc in neighbors_coords:
                        if 0 <= nr < rows and 0 <= nc < cols:
                            neighbor_assembly = self.State.reactor_matrix[nr][nc]
                            if neighbor_assembly != 0:
                                total_insertion += neighbor_assembly[z].insertion
                                valid_count += 1
                                
                    effective_insertion = total_insertion / valid_count
                    local_keff = node.GetKeff(effective_insertion)
                    
                    local_change = n_current * (local_keff - 1.0) * delta_t
                    source_injection = node.startup_source * delta_t
                    
                    net_diffusion = 0.0
                    for nr, nc in neighbors_coords:
                        if 0 <= nr < rows and 0 <= nc < cols:
                            neighbor_assembly = self.State.reactor_matrix[nr][nc]
                            if neighbor_assembly != 0:
                                net_diffusion += (neighbor_assembly[z].neutron_population - n_current) * radial_diffusion_rate
                            else:
                                net_diffusion -= n_current * (radial_diffusion_rate * 0.15)
                        else:
                            net_diffusion -= n_current * (radial_diffusion_rate * 0.15)
                            
                    if z > 0:
                        net_diffusion += (assembly[z-1].neutron_population - n_current) * axial_diffusion_rate
                    else:
                        net_diffusion -= n_current * (axial_diffusion_rate * 0.2)
                        
                    if z < self.State.num_slices - 1:
                        net_diffusion += (assembly[z+1].neutron_population - n_current) * axial_diffusion_rate
                    else:
                        net_diffusion -= n_current * (axial_diffusion_rate * 0.2)
                        
                    delta_n_matrix[r][c][z] = local_change + source_injection + net_diffusion

        # Update neutron populations
        for r in range(rows):
            for c in range(cols):
                assembly = self.State.reactor_matrix[r][c]
                if assembly != 0:
                    for z in range(self.State.num_slices):
                        assembly[z].neutron_population = max(0.0, assembly[z].neutron_population + delta_n_matrix[r][c][z])

        world.SimulationStateRegistry.SetState("reactor",self.State) #unsure if required