import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os

class UMLDiagramGenerator:
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
    
    def create_class_diagram(self, analysis):
        """Generate UML class diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        
        classes = []
        y_offset = 0.9
        x_positions = [0.1, 0.4, 0.7]  # Three columns
        col_index = 0
        
        # Extract classes from analysis
        for file_path, file_info in analysis['files'].items():
            for class_info in file_info.get('classes', []):
                if col_index >= len(x_positions):
                    col_index = 0
                    y_offset -= 0.25
                
                x_pos = x_positions[col_index]
                
                # Draw class box
                class_box = FancyBboxPatch(
                    (x_pos, y_offset), 0.25, 0.15,
                    boxstyle="round,pad=0.01",
                    facecolor='lightblue',
                    edgecolor='black',
                    linewidth=1.5
                )
                ax.add_patch(class_box)
                
                # Add class name
                ax.text(x_pos + 0.125, y_offset + 0.12, class_info['name'], 
                       ha='center', va='center', fontsize=10, fontweight='bold')
                
                # Add methods count
                methods_text = f"Methods: {class_info.get('methods', 0)}"
                ax.text(x_pos + 0.125, y_offset + 0.08, methods_text,
                       ha='center', va='center', fontsize=8)
                
                # Add file info
                file_text = f"File: {os.path.basename(file_path)}"
                ax.text(x_pos + 0.125, y_offset + 0.04, file_text,
                       ha='center', va='center', fontsize=7, style='italic')
                
                classes.append({
                    'name': class_info['name'],
                    'x': x_pos + 0.125,
                    'y': y_offset + 0.075,
                    'file': file_path
                })
                
                col_index += 1
        
        # Draw relationships (simplified)
        for i, class1 in enumerate(classes):
            for j, class2 in enumerate(classes[i+1:], i+1):
                if class1['file'] == class2['file']:  # Same file relationship
                    ax.annotate('', xy=(class2['x'], class2['y']), 
                               xytext=(class1['x'], class1['y']),
                               arrowprops=dict(arrowstyle='->', color='red', lw=1))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('UML Class Diagram', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        diagram_path = os.path.join(self.temp_dir, 'uml_class_diagram.png')
        plt.savefig(diagram_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return diagram_path
    
    def create_sequence_diagram(self, analysis):
        """Generate UML sequence diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Extract main functions/methods
        actors = []
        for file_path, file_info in analysis['files'].items():
            for func in file_info.get('functions', [])[:3]:  # Top 3 functions
                actors.append(f"{os.path.basename(file_path)}.{func['name']}")
        
        if not actors:
            actors = ['Main', 'Service', 'Database']  # Default actors
        
        # Draw lifelines
        x_positions = [i * 0.8 / len(actors) + 0.1 for i in range(len(actors))]
        
        for i, (actor, x_pos) in enumerate(zip(actors, x_positions)):
            # Actor box
            actor_box = FancyBboxPatch(
                (x_pos - 0.05, 0.9), 0.1, 0.08,
                boxstyle="round,pad=0.01",
                facecolor='lightgreen',
                edgecolor='black'
            )
            ax.add_patch(actor_box)
            ax.text(x_pos, 0.94, actor, ha='center', va='center', fontsize=8, fontweight='bold')
            
            # Lifeline
            ax.plot([x_pos, x_pos], [0.9, 0.1], 'k--', alpha=0.5)
        
        # Draw sample interactions
        y_pos = 0.8
        for i in range(min(5, len(actors)-1)):  # Sample interactions
            start_x = x_positions[i]
            end_x = x_positions[i+1] if i+1 < len(actors) else x_positions[0]
            
            ax.annotate('', xy=(end_x, y_pos), xytext=(start_x, y_pos),
                       arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))
            
            ax.text((start_x + end_x) / 2, y_pos + 0.02, f'call_{i+1}()',
                   ha='center', va='bottom', fontsize=8)
            
            y_pos -= 0.15
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('UML Sequence Diagram', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        seq_path = os.path.join(self.temp_dir, 'uml_sequence_diagram.png')
        plt.savefig(seq_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return seq_path

def create_data_flow_diagram(analysis, temp_dir):
    """Create data flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Define data flow components
    components = {
        'User Interface': (0.1, 0.8, 'lightblue'),
        'Business Logic': (0.5, 0.8, 'lightgreen'), 
        'Data Access': (0.9, 0.8, 'lightyellow'),
        'Database': (0.9, 0.4, 'lightcoral'),
        'External APIs': (0.1, 0.4, 'lightgray')
    }
    
    # Draw components
    for comp_name, (x, y, color) in components.items():
        if comp_name == 'Database':
            # Draw cylinder for database
            ellipse1 = patches.Ellipse((x, y+0.05), 0.15, 0.05, facecolor=color, edgecolor='black')
            rect = patches.Rectangle((x-0.075, y-0.05), 0.15, 0.1, facecolor=color, edgecolor='black')
            ellipse2 = patches.Ellipse((x, y-0.05), 0.15, 0.05, facecolor=color, edgecolor='black')
            
            ax.add_patch(rect)
            ax.add_patch(ellipse1)
            ax.add_patch(ellipse2)
        else:
            # Draw rectangle for other components
            rect = FancyBboxPatch(
                (x-0.075, y-0.05), 0.15, 0.1,
                boxstyle="round,pad=0.01",
                facecolor=color,
                edgecolor='black'
            )
            ax.add_patch(rect)
        
        ax.text(x, y, comp_name, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Draw data flows
    flows = [
        ('User Interface', 'Business Logic', 'User Input'),
        ('Business Logic', 'Data Access', 'Query'),
        ('Data Access', 'Database', 'SQL'),
        ('Business Logic', 'External APIs', 'API Call'),
        ('Business Logic', 'User Interface', 'Response')
    ]
    
    for source, target, label in flows:
        if source in components and target in components:
            x1, y1, _ = components[source]
            x2, y2, _ = components[target]
            
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
            
            # Add label
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y + 0.03, label, ha='center', va='bottom', 
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Data Flow Diagram', fontsize=16, fontweight='bold')
    ax.axis('off')
    
    dfd_path = os.path.join(temp_dir, 'data_flow_diagram.png')
    plt.savefig(dfd_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return dfd_path
