async function openPopup() {
    // 1. Call the Python function
    const response = await fetch('/api/generate');
    const data = await response.json();

    // 2. Find your popup elements
    const modal = document.getElementById("myModal");
    const imgElement = document.getElementById("popupImage");

    // 3. Set the image source to the Base64 string from Python
    imgElement.src = `data:image/png;base64,${data.image}`;

    // 4. Show the popup
    modal.style.display = "block";
}