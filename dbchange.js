const tasks = require('./tasks.json');
const fs = require('fs');

const find = (field, value) => {
  const findingTask = tasks.filter((task) => {
    return task[field] == value;
  });
  console.log(findingTask);

  return findingTask;
};

const update = (id, field, value) => {
  const findingTask = tasks.filter((task) => {
    return task.id == id;
  });

  findingTask[0][field] = value;
  fs.writeFile('./tasks.json', JSON.stringify(tasks, null, 2), (err) => {
    console.log(err);
  });
  return findingTask;
}

// update(2, "id", 9);
update(9, "description", "new updated description");

find("id", 2);