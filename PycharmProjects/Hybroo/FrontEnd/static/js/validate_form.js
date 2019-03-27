function validateForm() {
  var type_of_problem = document.forms["main-form"]["type_of_problem"].value;

  if (type_of_problem == 'vrp') {
    instance_selected_vrp = document.forms["main-form"]["instance_selected_vrp"].value;
    if (instance_selected_vrp == ''){
        alert("Select the VRP Instance!");
        return false;
    }
  }else{
    instance_selected_tsp = document.forms["main-form"]["instance_selected_tsp"].value;
    if (instance_selected_tsp == ''){
        alert("Select the TSP Instance!");
        return false;
    }
  }
  var type_of_method = document.forms["main-form"]["type_of_method"].value;
  if (type_of_method == ''){
    alert("Select the type of approach!");
    return false;
  }

  method_selected_1 = document.forms["main-form"]["method_selected_1"].value;
  if (method_selected_1 == ''){
      alert("Select the first method!");
      return false;
  }

  if (type_of_method == 'hybrid') {
    method_selected_2 = document.forms["main-form"]["method_selected_2"].value;
    if (method_selected_2 == ''){
      alert("Select the second method!");
      return false;
    }
  }
  return true;

}