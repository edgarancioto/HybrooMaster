function init_instance(){
    type_of_problem_change_instance();
    type_of_method_change_instance();
}

function type_of_problem_change_instance(){
    var tsp = document.getElementById("tsp-list");
    var vrp = document.getElementById("vrp-list");
    var radio = document.getElementById("radio_type_of_problem_1");
    if (radio.checked) {
        vrp.style.display = "block";
        tsp.style.display = "none";
    } else {
        vrp.style.display = "none";
        tsp.style.display = "block";
    }
}

function type_of_method_change_instance(){
    var radio_type_of_problem_1 = document.getElementById("radio_type_of_problem_1");
    var radio_type_of_method_1 = document.getElementById("radio_type_of_method_1");

    var method_selected_1 = document.getElementById("method-selected-1");
    var method_selected_2 = document.getElementById("method-selected-2");

    var ga_tsp_panel = document.getElementById("ga-tsp-panel");
    var ga_vrp_panel = document.getElementById("ga-vrp-panel");
    var aco_panel = document.getElementById("aco-panel");
    var sa_panel = document.getElementById("sa-panel");

    method_selected_1.style.display = "none";
    method_selected_2.style.display = "none";
    ga_tsp_panel.style.display = "none";
    ga_vrp_panel.style.display = "none";
    aco_panel.style.display = "none";
    sa_panel.style.display = "none";

    if (radio_type_of_method_1.checked || radio_type_of_method_2.checked){
        method_selected_1.style.display = "inline";

        if (method_selected_1.value == 'Ant Colony Optimization')
            aco_panel.style.display = "inline-block";
        else
            if (method_selected_1.value == 'Genetic Algorithm'){
                if (radio_type_of_problem_1.checked)
                    ga_vrp_panel.style.display = "inline-block";

                else
                    ga_tsp_panel.style.display = "inline-block";

            }else
                if (method_selected_1.value == 'Simulated Annealing')
                    sa_panel.style.display = "inline-block";

        if(radio_type_of_method_2.checked){
            method_selected_2.style.display = "inline";

            if (method_selected_2.value == 'Genetic Algorithm'){
                if (radio_type_of_problem_1.checked)
                    ga_vrp_panel.style.display = "inline-block";
                else
                    ga_tsp_panel.style.display = "inline-block";
            }else
                if (method_selected_2.value == 'Simulated Annealing')
                    sa_panel.style.display = "inline-block";
        }
    }
}

function type_of_method_change_function(){
    var radio_type_of_method_1 = document.getElementById("radio_type_of_method_1");

    var method_selected_1 = document.getElementById("method-selected-1");
    var method_selected_2 = document.getElementById("method-selected-2");

    var ga_panel = document.getElementById("ga-panel");
    var sa_panel = document.getElementById("sa-panel");

    method_selected_1.style.display = "none";
    method_selected_2.style.display = "none";
    ga_panel.style.display = "none";
    sa_panel.style.display = "none";

    if (radio_type_of_method_1.checked || radio_type_of_method_2.checked){
        method_selected_1.style.display = "inline";

        if (method_selected_1.value == 'Genetic Algorithm'){
            ga_panel.style.display = "inline-block";
        }else{
            if (method_selected_1.value == 'Simulated Annealing')
                sa_panel.style.display = "inline-block";
        }
        if(radio_type_of_method_2.checked){
            method_selected_2.style.display = "inline";
            if (method_selected_2.value == 'Genetic Algorithm'){
                ga_panel.style.display = "inline-block";
            }else{
                if (method_selected_2.value == 'Simulated Annealing')
                    sa_panel.style.display = "inline-block";
            }
        }
    }
}
