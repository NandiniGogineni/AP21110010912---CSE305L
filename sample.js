function changeState(selectElement) {

  var row = selectElement.parentNode.parentNode;

  var suggestionTextarea = row.querySelector('textarea');

  // Get the selected state
  var selectedState = selectElement.value;

  if (selectedState === 'In Progress') {
    suggestionTextarea.disabled = false;
    suggestionTextarea.style.display = 'block';
  } else {
    suggestionTextarea.disabled = true;
    suggestionTextarea.value = '';
    suggestionTextarea.style.display = 'none';
  }
}
