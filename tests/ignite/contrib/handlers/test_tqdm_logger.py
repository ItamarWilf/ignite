# -*- coding: utf-8 -*-
import numpy as np
import pytest
import torch

from ignite.contrib.handlers import ProgressBar
from ignite.engine import Engine, Events
from ignite.metrics import RunningAverage
from ignite.contrib.handlers import CustomPeriodicEvent
from ignite.handlers import TerminateOnNan


def update_fn(engine, batch):
    a = 1
    engine.state.metrics['a'] = a
    return a


def test_pbar(capsys):

    n_epochs = 2
    loader = [1, 2]
    engine = Engine(update_fn)

    pbar = ProgressBar()
    pbar.attach(engine, ['a'])

    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'Epoch [2/2]: [1/2]  50%|█████     , a=1.00e+00 [00:00<00:00]'
    assert err[-1] == expected


def test_pbar_log_message(capsys):

    ProgressBar.log_message("test")

    captured = capsys.readouterr()
    out = captured.out.split('\r')
    out = list(map(lambda x: x.strip(), out))
    out = list(filter(None, out))
    expected = u'test'
    assert out[-1] == expected


def test_attach_fail_with_string():
    engine = Engine(update_fn)
    pbar = ProgressBar()

    with pytest.raises(TypeError):
        pbar.attach(engine, 'a')


def test_pbar_with_metric(capsys):

    n_iters = 2
    data = list(range(n_iters))
    loss_values = iter(range(n_iters))

    def step(engine, batch):
        loss_value = next(loss_values)
        return loss_value

    trainer = Engine(step)

    RunningAverage(alpha=0.5, output_transform=lambda x: x).attach(trainer, "batchloss")

    pbar = ProgressBar()
    pbar.attach(trainer, metric_names=['batchloss', ])

    trainer.run(data=data, max_epochs=1)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    actual = err[-1]
    expected = u'Epoch: [1/2]  50%|█████     , batchloss=5.00e-01 [00:00<00:00]'
    assert actual == expected


def test_pbar_with_all_metric(capsys):

    n_iters = 2
    data = list(range(n_iters))
    loss_values = iter(range(n_iters))
    another_loss_values = iter(range(1, n_iters + 1))

    def step(engine, batch):
        loss_value = next(loss_values)
        another_loss_value = next(another_loss_values)
        return loss_value, another_loss_value

    trainer = Engine(step)

    RunningAverage(alpha=0.5, output_transform=lambda x: x[0]).attach(trainer, "batchloss")
    RunningAverage(alpha=0.5, output_transform=lambda x: x[1]).attach(trainer, "another batchloss")

    pbar = ProgressBar()
    pbar.attach(trainer, metric_names="all")

    trainer.run(data=data, max_epochs=1)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    actual = err[-1]
    expected = u'Epoch: [1/2]  50%|█████     , another batchloss=1.50e+00, batchloss=5.00e-01 [00:00<00:00]'
    assert actual == expected


def test_pbar_no_metric_names(capsys):

    n_epochs = 2
    loader = [1, 2]
    engine = Engine(update_fn)

    pbar = ProgressBar()
    pbar.attach(engine)

    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    actual = err[-1]
    expected = u'Epoch [2/2]: [1/2]  50%|█████      [00:00<00:00]'
    assert actual == expected


def test_pbar_with_output(capsys):
    n_epochs = 2
    loader = [1, 2]
    engine = Engine(update_fn)

    pbar = ProgressBar()
    pbar.attach(engine, output_transform=lambda x: {'a': x})

    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'Epoch [2/2]: [1/2]  50%|█████     , a=1.00e+00 [00:00<00:00]'
    assert err[-1] == expected


def test_pbar_fail_with_non_callable_transform():
    engine = Engine(update_fn)
    pbar = ProgressBar()

    with pytest.raises(TypeError):
        pbar.attach(engine, output_transform=1)


def test_pbar_with_scalar_output(capsys):
    n_epochs = 2
    loader = [1, 2]
    engine = Engine(update_fn)

    pbar = ProgressBar()
    pbar.attach(engine, output_transform=lambda x: x)

    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'Epoch [2/2]: [1/2]  50%|█████     , output=1.00e+00 [00:00<00:00]'
    assert err[-1] == expected


def test_pbar_with_str_output(capsys):
    n_epochs = 2
    loader = [1, 2]
    engine = Engine(update_fn)

    pbar = ProgressBar()
    pbar.attach(engine, output_transform=lambda x: "red")

    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'Epoch [2/2]: [1/2]  50%|█████     , output=red [00:00<00:00]'
    assert err[-1] == expected


def test_pbar_with_tqdm_kwargs(capsys):
    n_epochs = 10
    loader = [1, 2, 3, 4, 5]
    engine = Engine(update_fn)

    pbar = ProgressBar(desc="My description: ")
    pbar.attach(engine, output_transform=lambda x: x)
    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'My description:  [10/10]: [4/5]  80%|████████  , output=1.00e+00 [00:00<00:00]'.format()
    assert err[-1] == expected


def test_pbar_for_validation(capsys):
    loader = [1, 2, 3, 4, 5]
    engine = Engine(update_fn)

    pbar = ProgressBar(desc="Validation")
    pbar.attach(engine)
    engine.run(loader, max_epochs=1)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'Validation: [4/5]  80%|████████   [00:00<00:00]'
    assert err[-1] == expected


def test_pbar_output_tensor(capsys):
    loader = [1, 2, 3, 4, 5]

    def update_fn(engine, batch):
        return torch.Tensor([batch, 0])

    engine = Engine(update_fn)

    pbar = ProgressBar(desc="Output tensor")
    pbar.attach(engine, output_transform=lambda x: x)
    engine.run(loader, max_epochs=1)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    expected = u'Output tensor: [4/5]  80%|████████  , output_0=5.00e+00, output_1=0.00e+00 [00:00<00:00]'
    assert err[-1] == expected


def test_pbar_output_warning(capsys):
    loader = [1, 2, 3, 4, 5]

    def update_fn(engine, batch):
        return batch, "abc"

    engine = Engine(update_fn)

    pbar = ProgressBar(desc="Output tensor")
    pbar.attach(engine, output_transform=lambda x: x)
    with pytest.warns(UserWarning):
        engine.run(loader, max_epochs=1)


def test_pbar_on_epochs(capsys):

    n_epochs = 10
    loader = [1, 2, 3, 4, 5]
    engine = Engine(update_fn)

    pbar = ProgressBar()
    pbar.attach(engine, event_name=Events.EPOCH_STARTED, closing_event_name=Events.COMPLETED)
    engine.run(loader, max_epochs=n_epochs)

    captured = capsys.readouterr()
    err = captured.err.split('\r')
    err = list(map(lambda x: x.strip(), err))
    err = list(filter(None, err))
    actual = err[-1]
    expected = u'Epoch: [9/10]  90%|█████████  [00:00<00:00]'
    assert actual == expected


def test_pbar_wrong_events_order():

    engine = Engine(update_fn)
    pbar = ProgressBar()

    with pytest.raises(ValueError, match="should be called before closing event"):
        pbar.attach(engine, event_name=Events.COMPLETED, closing_event_name=Events.COMPLETED)

    with pytest.raises(ValueError, match="should be called before closing event"):
        pbar.attach(engine, event_name=Events.COMPLETED, closing_event_name=Events.EPOCH_COMPLETED)

    with pytest.raises(ValueError, match="should be called before closing event"):
        pbar.attach(engine, event_name=Events.COMPLETED, closing_event_name=Events.ITERATION_COMPLETED)

    with pytest.raises(ValueError, match="should be called before closing event"):
        pbar.attach(engine, event_name=Events.EPOCH_COMPLETED, closing_event_name=Events.EPOCH_COMPLETED)

    with pytest.raises(ValueError, match="should be called before closing event"):
        pbar.attach(engine, event_name=Events.ITERATION_COMPLETED, closing_event_name=Events.ITERATION_STARTED)


def test_pbar_on_custom_events(capsys):

    engine = Engine(update_fn)
    pbar = ProgressBar()
    cpe = CustomPeriodicEvent(n_iterations=15)

    with pytest.raises(ValueError, match=r"Logging and closing events should be only ignite.engine.Events"):
        pbar.attach(engine, event_name=cpe.Events.ITERATIONS_15_COMPLETED, closing_event_name=Events.EPOCH_COMPLETED)


def test_pbar_with_nan_input():
    def update(engine, batch):
        x = batch
        return x.item()

    def create_engine():
        engine = Engine(update)
        pbar = ProgressBar()

        engine.add_event_handler(Events.ITERATION_COMPLETED, TerminateOnNan())
        pbar.attach(engine, event_name=Events.EPOCH_COMPLETED, closing_event_name=Events.COMPLETED)
        return engine

    data = torch.from_numpy(np.array([np.nan] * 25))
    engine = create_engine()
    engine.run(data)
    assert engine.should_terminate
    assert engine.state.iteration == 1
    assert engine.state.epoch == 1

    data = torch.from_numpy(np.array([1] * 1000 + [np.nan] * 25))
    engine = create_engine()
    engine.run(data)
    assert engine.should_terminate
    assert engine.state.iteration == 1001
    assert engine.state.epoch == 1
