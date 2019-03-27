function inform_function(){
    var radio_benchmark = document.getElementById("radio_benchmark");
    var benchmark_panel = document.getElementById("benchmark-panel");
    var modeling_panel = document.getElementById("modeling-panel");
    benchmark_panel.style.display = "none";
    modeling_panel.style.display = "none";

    if (radio_benchmark.checked)
        benchmark_panel.style.display = "inline-block";
    else
        modeling_panel.style.display = "inline-block";
}